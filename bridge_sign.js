const path = require('path');
const fs = require('fs');
global.CryptoJs = require('crypto-js');

// 技能包根目录 = 本文件所在目录（动态解析，可随项目移动）
const skDir = __dirname;
const staticDir = path.join(skDir, 'static');

// ---- 签名：xhs_main_260411.js ----
const mainCode = fs.readFileSync(path.join(staticDir, 'xhs_main_260411.js'), 'utf-8');
const patchedMain = mainCode.replace(
    'var CryptoJs = require("crypto-js");',
    'var CryptoJs = global.CryptoJs;'
);
eval(patchedMain);

// ---- xray traceId：xhs_xray.js + pack1/pack2（webpack chunk）----
global.self = global;
global.window = global;
self.webpackChunkxhs_pc_web = [];

function fakeRequire(mod) {
    let file = mod;
    if (file.startsWith('./static/')) file = file.replace('./static/', '');
    if (file.startsWith('../static/')) file = file.replace('../static/', '');
    if (file.startsWith('./')) file = file.replace('./', '');
    const full = path.join(staticDir, file);
    if (!fs.existsSync(full)) { throw new Error('xray dep not found: ' + full); }
    (0, eval)(fs.readFileSync(full, 'utf-8'));
    return {};
}
try {
    const xrayCode = fs.readFileSync(path.join(staticDir, 'xhs_xray.js'), 'utf-8');
    const xrayFn = new Function('require', xrayCode);
    xrayFn(fakeRequire);
} catch (e) {
    // xray optional; sign still works
}

// Read stdin
let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
    try {
        const args = JSON.parse(input);
        let result;
        if (args.cmd === 'traceid') {
            result = { traceId: (typeof traceId === 'function') ? traceId() : '' };
        } else {
            result = get_request_headers_params(args.api, args.data, args.a1, args.method || 'POST');
        }
        process.stdout.write(JSON.stringify(result));
    } catch (e) {
        process.stderr.write('JS_ERROR: ' + e.message + '\n');
        process.exit(1);
    }
});
