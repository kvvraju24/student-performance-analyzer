const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const fixture = fs.readFileSync(path.join(__dirname, 'fixtures/students.csv'), 'utf8');
const dataset = fs.readFileSync(path.join(root, 'StudentsPerformance.csv'), 'utf8');

async function dashboard(csv = fixture, ok = true) {
    const elements = new Map();
    const context = vm.createContext({
        document: { getElementById(id) {
            if (!elements.has(id)) elements.set(id, {
                value: '', textContent: '', innerHTML: '', disabled: false, style: {}, listeners: {},
                addEventListener(event, handler) { this.listeners[event] = handler; }
            });
            return elements.get(id);
        } },
        fetch: async () => ({ ok, text: async () => csv }),
        console: { error() {} }
    });
    vm.runInContext(fs.readFileSync(path.join(root, 'dashboard.js'), 'utf8'), context);
    await new Promise(resolve => setImmediate(resolve));
    return { elements, run: code => vm.runInContext(code, context) };
}

test('fixture metrics agree with Python and group sizes are displayed', async () => {
    const { elements } = await dashboard();
    assert.equal(elements.get('count').textContent, '2');
    assert.equal(elements.get('average').textContent, '70.0');
    assert.equal(elements.get('pass').textContent, '50%');
    assert.match(elements.get('bars').innerHTML, /n=1/);
});

test('real data, dropdowns, search, pagination, empty state and reset', async () => {
    const { elements: e } = await dashboard(dataset);
    assert.equal(e.get('count').textContent, '1,000');
    assert.equal(e.get('average').textContent, '67.8');
    assert.equal(e.get('pass').textContent, '81%');
    assert.equal(e.get('top').textContent, 'Reading');
    e.get('next').listeners.click();
    assert.match(e.get('page').textContent, /Page 2 of 84/);
    e.get('gender').value = 'female'; e.get('gender').listeners.change();
    assert.equal(e.get('count').textContent, '518');
    e.get('search').value = 'no-such-record'; e.get('search').listeners.input();
    assert.match(e.get('table').innerHTML, /No records found/);
    assert.equal(e.get('count').textContent, '518');
    e.get('reset').listeners.click();
    assert.equal(e.get('search').value, '');
    assert.equal(e.get('gender').value, '');
    assert.equal(e.get('count').textContent, '1,000');
    assert.match(e.get('page').textContent, /Page 1 of 84/);
    e.get('gender').value = 'unknown'; e.get('gender').listeners.change();
    assert.equal(e.get('average').textContent, '—');
    assert.match(e.get('bars').innerHTML, /No students match/);
});

test('histogram includes 100 and fractional averages in correct intervals', async () => {
    const { run, elements } = await dashboard();
    run('filtered = [{ "math score": "100", "reading score": "100", "writing score": "100" }]; renderDistribution();');
    assert.match(elements.get('distribution').innerHTML, /90–100:\s+1 students/);
    assert.match(elements.get('distribution').innerHTML, /0–<10/);
});

test('reject invalid scores, headers, empty input and malformed quoting', async () => {
    const { run } = await dashboard();
    for (const bad of ['', fixture.split('\n')[0], fixture.replace('math score', 'other'),
                       fixture.replace('writing score', 'writing score,total score'),
                       fixture.replace('100,90,80', '101,90,80'), fixture.replace('100,90,80', '-1,90,80'),
                       fixture.replace('100,90,80', ',90,80'), fixture.replace('100,90,80', '70.5,90,80'),
                       fixture + '\n"unfinished', fixture.replace('100,90,80', '"100"oops,90,80')]) {
        assert.throws(() => run(`csvParse(${JSON.stringify(bad)})`));
    }
});

test('BOM, quoted commas, CRLF and escaped quotes are handled', async () => {
    const { run } = await dashboard();
    const csv = '\uFEFF' + fixture.replace("bachelor's degree", '"degree, with ""honors"""').replaceAll('\n', '\r\n');
    assert.equal(run(`csvParse(${JSON.stringify(csv)})[0]["parental level of education"]`), 'degree, with "honors"');
});

test('dataset markup is escaped before rendering', async () => {
    const { elements } = await dashboard(fixture.replace('female', '<img src=x onerror=alert(1)>'));
    assert.doesNotMatch(elements.get('table').innerHTML, /<img/);
    assert.match(elements.get('table').innerHTML, /&lt;img/);
});

test('data load failures and invalid CSV show an error', async () => {
    for (const [csv, ok] of [[fixture, false], ['invalid', true]]) {
        const { elements } = await dashboard(csv, ok);
        assert.equal(elements.get('error').style.display, 'block');
        assert.match(elements.get('error').textContent, /Could not load student data/);
    }
});

test('expanded synthetic data renders eight subject columns and 5000 records', async () => {
    const csv = fs.readFileSync(path.join(root, 'data/synthetic_students.csv'), 'utf8');
    const { elements, run } = await dashboard(csv);
    assert.equal(elements.get('count').textContent, '5,000');
    assert.equal(run('scoreFields.length'), 8);
    assert.match(elements.get('student-columns').innerHTML, /Computer Science/);
    assert.match(elements.get('student-columns').innerHTML, /History/);
    const expected = csv.trim().split('\n')[1].split(',').slice(-8).map(Number).reduce((a,b) => a+b, 0) / 8;
    assert.equal(run('overall(data[0])'), expected);
    assert.equal((elements.get('table').innerHTML.match(/class="num"/g) || []).length, 12 * 8);
});
