# WebGAL 部署上线

> WebGAL 构建产出的 `dist/` 为标准静态站点，可部署到任意静态托管服务。

## 部署方式

### 方式 1: 静态站点托管（推荐）

```
Netlify:  拖拽 dist/ 到 Netlify Drop → 自动 HTTPS + CDN
Vercel:   vercel deploy dist/ → 自动 HTTPS + CDN  
GitHub Pages: 推送 dist/ 到 gh-pages 分支
Cloudflare Pages: 连接 Git 仓库 → 自动构建 + 部署
```

### 方式 2: 自有服务器 Nginx

```nginx
server {
    listen 443 ssl;
    server_name game.{domain};
    root /var/www/{game-key}/dist;
    index index.html;
}
```

```powershell
scp -r dist/ user@server:/var/www/{game-key}/
```

### 方式 3: Publish CLI 工具

如有 publish 命令行工具可用：

```powershell
publish config init
publish deploy {game-key} -d {domain} -w dist/
```

## 部署前检查

- proof bundle 人工确认通过
- `dist/index.html` 存在并可访问
- 所有素材路径为相对路径
- `dist/` 总体积 < 50MB

## 部署约束

- 项目名只支持小写字母、数字、连字符
- SSL 证书申请需要时间（首次部署子域名需等待）
- 同域名多次部署使用 `--force` 覆盖
