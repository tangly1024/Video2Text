#!/usr/bin/env node
"use strict";

const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const os = require("os");
const path = require("path");

const root = path.resolve(__dirname, "..");
const htmlPath = path.join(__dirname, "web-ui.html");
const port = Number(process.env.PORT || 8766);
const host = process.env.HOST || "127.0.0.1";

function sendJson(res, status, payload) {
  const body = Buffer.from(JSON.stringify(payload), "utf8");
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "content-length": body.length,
  });
  res.end(body);
}

function parseMultipart(req, body) {
  const type = req.headers["content-type"] || "";
  const match = type.match(/boundary=(?:"([^"]+)"|([^;]+))/);
  if (!match) throw new Error("missing multipart boundary");
  const boundary = Buffer.from(`--${match[1] || match[2]}`);
  const fields = {};
  let file = null;
  let start = body.indexOf(boundary);
  while (start !== -1) {
    start += boundary.length;
    if (body[start] === 45 && body[start + 1] === 45) break;
    if (body[start] === 13 && body[start + 1] === 10) start += 2;
    const headerEnd = body.indexOf(Buffer.from("\r\n\r\n"), start);
    if (headerEnd === -1) break;
    const headers = body.slice(start, headerEnd).toString("utf8");
    let partEnd = body.indexOf(boundary, headerEnd + 4);
    if (partEnd === -1) break;
    let content = body.slice(headerEnd + 4, partEnd);
    if (content.length >= 2 && content[content.length - 2] === 13 && content[content.length - 1] === 10) {
      content = content.slice(0, -2);
    }
    const name = /name="([^"]+)"/.exec(headers)?.[1];
    const filename = /filename="([^"]*)"/.exec(headers)?.[1];
    if (name && filename) {
      file = { name, filename: path.basename(filename), content };
    } else if (name) {
      fields[name] = content.toString("utf8").trim();
    }
    start = partEnd;
  }
  return { fields, file };
}

function collectBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

function runVideo2Text(args) {
  return new Promise((resolve, reject) => {
    const command = process.env.VIDEO2TEXT_PYTHON || (process.platform === "win32" ? "python" : "python3");
    const child = spawn(command, ["main.py", ...args], {
      cwd: root,
      env: { ...process.env, PYTHONIOENCODING: "utf-8" },
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => { stdout += chunk.toString("utf8"); });
    child.stderr.on("data", (chunk) => { stderr += chunk.toString("utf8"); });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolve(stdout.trim());
      else reject(new Error(stderr.trim() || `video2text exited with ${code}`));
    });
  });
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === "GET" && (req.url === "/" || req.url === "/index.html" || req.url === "/web-ui.html")) {
      const body = fs.readFileSync(htmlPath);
      res.writeHead(200, { "content-type": "text/html; charset=utf-8", "content-length": body.length });
      res.end(body);
      return;
    }
    if (req.method === "GET" && req.url === "/api/status") {
      sendJson(res, 200, { ok: true, runtime: "node" });
      return;
    }
    if (req.method !== "POST" || req.url !== "/api/convert") {
      sendJson(res, 404, { ok: false, error: "not found" });
      return;
    }

    const { fields, file } = parseMultipart(req, await collectBody(req));
    if (!file) throw new Error("请选择音频或视频文件");

    const suffix = path.extname(file.filename) || ".media";
    const sourcePath = path.join(os.tmpdir(), `video2text-${Date.now()}${suffix}`);
    fs.writeFileSync(sourcePath, file.content);
    try {
      const output = fields.output || "output";
      const language = fields.language || "zh-CN";
      const segmentLength = fields.segmentLength || "30";
      const workers = fields.workers || "5";
      const textPath = await runVideo2Text([
        sourcePath,
        "-o", output,
        "--language", language,
        "--segment-length", segmentLength,
        "--workers", workers,
      ]);
      const text = fs.readFileSync(textPath, "utf8");
      sendJson(res, 200, { ok: true, path: textPath, text });
    } finally {
      fs.rmSync(sourcePath, { force: true });
    }
  } catch (error) {
    sendJson(res, 400, { ok: false, error: error.message });
  }
});

server.listen(port, host, () => {
  console.log(`Video2Text Node UI: http://${host}:${port}/`);
});
