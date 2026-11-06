// Cloudflare Worker：取代原本 Render 上的 FastAPI 後端
// 資料庫：Cloudflare D1（SQLite），圖片：ImgBB

const JSON_HEADERS = { "Content-Type": "application/json; charset=utf-8" };

function corsHeaders(env) {
  return {
    "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || "*",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };
}

function json(data, status, env) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...JSON_HEADERS, ...corsHeaders(env) },
  });
}

function isAuthorized(request, env) {
  const auth = request.headers.get("Authorization") || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
  return Boolean(token) && Boolean(env.SECRET_TOKEN) && token === env.SECRET_TOKEN;
}

function isValidProject(body) {
  return ["title", "image", "content", "date"].every((key) => typeof body[key] === "string");
}

async function handleLogin(request, env) {
  const body = await request.json().catch(() => null);
  if (!body || body.username !== env.ADMIN_USER || body.password !== env.ADMIN_PASSWORD) {
    return json({ detail: "wrong username or password" }, 401, env);
  }
  return json({ status: "success", message: "login successful", token: env.SECRET_TOKEN }, 200, env);
}

async function listProjects(env) {
  const { results } = await env.DB.prepare(
    "SELECT id, title, image, content, date FROM projects ORDER BY id ASC"
  ).all();
  return json(results, 200, env);
}

async function createProject(request, env) {
  const body = await request.json().catch(() => null);
  if (!body || !isValidProject(body)) {
    return json({ detail: "invalid project data" }, 400, env);
  }
  await env.DB.prepare(
    "INSERT INTO projects (title, image, content, date) VALUES (?, ?, ?, ?)"
  )
    .bind(body.title, body.image, body.content, body.date)
    .run();
  return json({ status: "success", message: "create success" }, 201, env);
}

async function deleteProject(id, env) {
  const result = await env.DB.prepare("DELETE FROM projects WHERE id = ?").bind(id).run();
  if (result.meta.changes === 0) {
    return json({ detail: "not found" }, 404, env);
  }
  return json({ status: "success", message: "delete success" }, 200, env);
}

const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

// 把 ArrayBuffer 轉成 base64。分段處理，避免大檔案把呼叫堆疊塞爆
function toBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  const CHUNK = 0x8000;
  let binary = "";
  for (let i = 0; i < bytes.length; i += CHUNK) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + CHUNK));
  }
  return btoa(binary);
}

async function uploadImage(request, env) {
  const form = await request.formData().catch(() => null);
  const file = form && form.get("file");
  if (!file || typeof file === "string") {
    return json({ detail: "file is required" }, 400, env);
  }
  if (!file.type.startsWith("image/")) {
    return json({ detail: "only image files are allowed" }, 400, env);
  }
  if (file.size > MAX_IMAGE_BYTES) {
    return json({ detail: "image must be 5MB or smaller" }, 413, env);
  }

  const payload = new URLSearchParams();
  payload.append("key", env.IMGBB_API_KEY);
  payload.append("image", toBase64(await file.arrayBuffer()));

  const res = await fetch("https://api.imgbb.com/1/upload", {
    method: "POST",
    body: payload,
  });

  if (!res.ok) {
    console.error("ImgBB denied request:", await res.text());
    return json({ detail: "image upload failed" }, 502, env);
  }

  const result = await res.json();
  return json({ status: "success", image_url: result.data.url }, 200, env);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const { pathname } = url;
    const method = request.method;

    if (method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(env) });
    }

    try {
      if (method === "GET" && pathname === "/") {
        return json({ message: "server is running!" }, 200, env);
      }

      if (method === "POST" && pathname === "/api/login") {
        return await handleLogin(request, env);
      }

      if (method === "GET" && pathname === "/api/projects") {
        return await listProjects(env);
      }

      if (method === "POST" && pathname === "/api/projects") {
        if (!isAuthorized(request, env)) return json({ detail: "access denied" }, 401, env);
        return await createProject(request, env);
      }

      const deleteMatch = pathname.match(/^\/api\/projects\/(\d+)$/);
      if (method === "DELETE" && deleteMatch) {
        if (!isAuthorized(request, env)) return json({ detail: "access denied" }, 401, env);
        return await deleteProject(Number(deleteMatch[1]), env);
      }

      if (method === "POST" && pathname === "/api/upload") {
        if (!isAuthorized(request, env)) return json({ detail: "access denied" }, 401, env);
        return await uploadImage(request, env);
      }

      return json({ detail: "not found" }, 404, env);
    } catch (err) {
      console.error(err);
      return json({ detail: `server error: ${err.message}` }, 500, env);
    }
  },
};
