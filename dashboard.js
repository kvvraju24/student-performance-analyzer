// Escape dataset text before inserting it into HTML templates.
function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[character]);
}

const fields = {
    gender: "gender",
    lunch: "lunch",
    prep: "test preparation course",
    race: "race/ethnicity",
    education: "parental level of education"
};
const scoreFields = [
    "math score",
    "reading score",
    "writing score"
];
const nice = {
    "math score": "Math",
    "reading score": "Reading",
    "writing score": "Writing"
};
let data = [];
let filtered = [];
let page = 1;
const perPage = 12;
const $ = id =>
    document.getElementById(id);
function csvParse(text) {
    text = text.replace(/^\uFEFF/, "");
    const rows = [];
    let row = [], cell = "", quoted = false, closedQuote = false;
    function finishRow() {
        row.push(cell);
        if (row.length > 1 || row[0].trim()) rows.push(row);
        row = []; cell = ""; closedQuote = false;
    }
    for (let i = 0; i < text.length; i++) {
        const c = text[i];
        if (quoted) {
            if (c === '"' && text[i + 1] === '"') { cell += '"'; i++; }
            else if (c === '"') { quoted = false; closedQuote = true; }
            else cell += c;
        } else if (c === ",") {
            row.push(cell); cell = ""; closedQuote = false;
        } else if (c === "\n" || c === "\r") {
            if (c === "\r" && text[i + 1] === "\n") i++;
            finishRow();
        } else if (closedQuote) {
            throw new Error("Unexpected text after a quoted CSV field.");
        } else if (c === '"') {
            if (cell) throw new Error("Unexpected quote in a CSV field.");
            quoted = true;
        } else cell += c;
    }
    if (quoted) throw new Error("CSV contains an unterminated quoted field.");
    if (cell || row.length || closedQuote) finishRow();
    const [headers = [], ...items] = rows;
    const required = [...Object.values(fields), ...scoreFields];
    const missing = required.filter(key => !headers.includes(key));
    if (missing.length) throw new Error("Missing required columns: " + missing.join(", "));
    if (new Set(headers).size !== headers.length) throw new Error("CSV headers must be unique.");
    if (!items.length) throw new Error("The CSV file contains no student records.");
    items.forEach((row, index) => {
        if (row.length !== headers.length) throw new Error(`CSV record ${index + 1}: column count does not match the header.`);
        required.forEach(key => {
            const value = row[headers.indexOf(key)].trim();
            if (!value) throw new Error(`CSV record ${index + 1}, column '${key}': value is required.`);
            if (scoreFields.includes(key) && (!/^[0-9]+$/.test(value) || Number(value) > 100)) {
                throw new Error(`CSV record ${index + 1}, column '${key}': expected an integer from 0 to 100.`);
            }
            row[headers.indexOf(key)] = value;
        });
    });
    return items.map(row =>
        Object.fromEntries(
            headers.map(
                (header, index) => [
                    header,
                    row[index] ?? ""
                ]
            )
        )
    );
}
function setup() {
    Object.entries(fields).forEach(
        ([id, key]) => {
            const element = $(id);
            element.innerHTML =
                '<option value="">All</option>' +
                [...new Set(
                    data.map(row => row[key])
                )]
                .sort()
                .map(
                    value =>
                    `<option>${escapeHtml(value)}</option>`
                )
                .join("");
            element.addEventListener(
                "change",
                () => {
                    page = 1;
                    render();
                }
            );
        }
    );
    const groupBy = $("groupBy");
    groupBy.innerHTML =
        Object.entries(fields)
        .map(
            ([id, key]) => {
                let name;
                if (id === "prep")
                    name = "Preparation Course";
                else if (id === "race")
                    name = "Race / Ethnicity";
                else if (id === "education")
                    name = "Parent Education";
                else
                    name =
                        id.charAt(0).toUpperCase()
                        + id.slice(1);
                return `
                    <option value="${key}">
                        ${name}
                    </option>
                `;
            }
        )
        .join("");
    groupBy.value =
        "test preparation course";
    groupBy.addEventListener(
        "change",
        render
    );
    $("search").addEventListener(
        "input",
        () => {
            page = 1;
            renderTable();
        }
    );
    $("reset").addEventListener(
        "click",
        () => {
            Object.keys(fields)
            .forEach(
                id => $(id).value = ""
            );
            $("search").value = "";
            page = 1;
            render();
        }
    );
    $("previous").addEventListener(
        "click",
        () => {
            if (page > 1) {
                page--;
                renderTable();
            }
        }
    );
    $("next").addEventListener(
        "click",
        () => {
            if (
                page < Math.ceil(
                    currentRows().length
                    / perPage
                )
            ) {
                page++;
                renderTable();
            }
        }
    );
    render();
}
function selected() {
    return data.filter(
        row =>
        Object.entries(fields)
        .every(
            ([id, key]) =>
                !$(id).value
                ||
                row[key] === $(id).value
        )
    );
}
function overall(row) {
    return (
        scoreFields.reduce(
            (sum, key) =>
                sum + Number(row[key]),
            0
        )
        / 3
    );
}
function avg(rows, key) {
    if (!rows.length)
        return 0;
    return rows.reduce(
        (sum, row) =>
            sum + Number(row[key]),
        0
    )
    / rows.length;
}
function render() {
    filtered = selected();
    const scores = scoreFields.map(
        key => ({
            key,
            value: avg(filtered, key)
        })
    );
    const total = filtered.length;
    const combined =
        scores.reduce(
            (sum, score) =>
                sum + score.value,
            0
        )
        / 3;
    const passed = total
        ?
        filtered.filter(
            row =>
            scoreFields.every(
                key =>
                Number(row[key]) >= 50
            )
        ).length
        / total
        * 100
        :
        0;
    const top =
        [...scores].sort(
            (a, b) =>
                b.value - a.value
        )[0];
    $("count").textContent =
        total.toLocaleString();
    $("average").textContent =
        total
        ? combined.toFixed(1)
        : "—";
    $("pass").textContent =
        total
        ? passed.toFixed(0) + "%"
        : "—";
    $("top").textContent =
        total
        ? nice[top.key]
        : "—";
    renderBars();
    renderSubjects(scores);
    renderDistribution();
    renderTable();
}
function renderBars() {
    const key =
        $("groupBy").value;
    const groups =
        [...new Set(
            filtered.map(
                row => row[key]
            )
        )]
        .sort()
        .map(
            name => {
                const rows =
                    filtered.filter(
                        row =>
                            row[key] === name
                    );
                return {
                    name,
                    count: rows.length,
                    avg:
                        (
                            avg(rows, "math score")
                            +
                            avg(rows, "reading score")
                            +
                            avg(rows, "writing score")
                        )
                        / 3
                };
            }
        )
        .sort(
            (a, b) =>
                b.avg - a.avg
        );
    if (!groups.length) {
        $("bars").innerHTML =
            '<div class="empty">No students match these filters.</div>';
        return;
    }
    $("bars").innerHTML =
        groups.map(
            group => `
                <div class="bar-row">
                    <span>
                        ${escapeHtml(group.name)} <small>(n=${group.count})</small>
                    </span>
                    <div class="track">
                        <div
                            class="fill"
                            style="width:${group.avg}%">
                        </div>
                    </div>
                    <strong>
                        ${group.avg.toFixed(1)}
                    </strong>
                </div>
            `
        ).join("");
}
function renderSubjects(scores) {
    const colors = [
        "#4263eb",
        "#099268",
        "#f08c00"
    ];
    $("subjects").innerHTML =
        scores.map(
            (score, index) => `
                <div class="score-row">
                    <span>
                        ${nice[score.key]}
                    </span>
                    <div class="track">
                        <div
                            class="fill"
                            style="
                                --c:${colors[index]};
                                width:${score.value}%;
                            ">
                        </div>
                    </div>
                    <strong>
                        ${score.value.toFixed(1)}
                    </strong>
                </div>
            `
        ).join("");
}
function renderDistribution() {
    const bins = Array.from(
        {length: 10},
        (_, index) => ({
            start: index * 10,
            label: index === 9 ? "90–100" : `${index * 10}–<${(index + 1) * 10}`,
            count: 0
        })
    );
    filtered.forEach(
        row => {
            const index = Math.min(
                9,
                Math.floor(
                    overall(row) / 10
                )
            );
            bins[index].count++;
        }
    );
    const max = Math.max(
        ...bins.map(
            bin => bin.count
        ),
        1
    );
    $("distribution").innerHTML =
        bins.map(
            bin => `
                <div
                    class="bin"
                    title="
                        ${bin.label}:
                        ${bin.count} students
                    "
                    style="
                        height:
                        ${(bin.count / max) * 100}%;
                    "
                >
                    <span>
                        ${bin.label}
                    </span>
                </div>
            `
        ).join("");
}
function currentRows() {
    const term =
        $("search")
        .value
        .trim()
        .toLowerCase();
    if (!term)
        return filtered;
    return filtered.filter(
        row =>
        Object.values(row)
        .some(
            value =>
                String(value)
                .toLowerCase()
                .includes(term)
        )
    );
}
function renderTable() {
    const rows =
        currentRows();
    const pages = Math.max(
        1,
        Math.ceil(
            rows.length / perPage
        )
    );
    if (page > pages)
        page = pages;
    const start =
        (page - 1)
        * perPage;
    const slice =
        rows.slice(
            start,
            start + perPage
        );
    if (!slice.length) {
        $("table").innerHTML = `
            <tr>
                <td
                    colspan="8"
                    class="empty"
                >
                    No records found.
                </td>
            </tr>
        `;
    }
    else {
        $("table").innerHTML =
            slice.map(
                row => `
                    <tr>
                        <td>
                            ${escapeHtml(row.gender)}
                        </td>
                        <td>
                            ${escapeHtml(row["race/ethnicity"])}
                        </td>
                        <td>
                            ${escapeHtml(row["parental level of education"])}
                        </td>
                        <td>
                            <span class="tag">
                                ${escapeHtml(row.lunch)}
                            </span>
                        </td>
                        <td>
                            ${escapeHtml(row["test preparation course"])}
                        </td>
                        <td class="num">
                            ${row["math score"]}
                        </td>
                        <td class="num">
                            ${row["reading score"]}
                        </td>
                        <td class="num">
                            ${row["writing score"]}
                        </td>
                    </tr>
                `
            ).join("");
    }
    $("page").textContent =
        `Page ${page} of ${pages} · ${rows.length} records`;
    $("previous").disabled =
        page === 1;
    $("next").disabled =
        page === pages;
}
/*
    DATASET CONNECTION
    index.html
         ↓
    StudentsPerformance.csv
*/
fetch("StudentsPerformance.csv")
.then(response => {
    if (!response.ok)
        throw new Error(
            "Dataset could not be loaded"
        );
    return response.text();
})
.then(text => {
    data = csvParse(text);
    setup();
})
.catch(error => {
    console.error(error);
    $("error").style.display =
        "block";
    $("error").textContent =
        `Could not load student data: ${error.message} Serve this folder with a local web server and check the CSV.`;
});
