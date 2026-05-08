# tixcraft 清票通知工具

> 這是「**監控活動頁面是否出現可購票訊號**」的小工具，不會自動下單。

## 功能
- 定時檢查拓元活動頁面內容變化
- 偵測到疑似可購票關鍵字時發出通知
- 支援 Discord Webhook 推播

## 安裝
```bash
python -m venv .venv
source .venv/bin/activate
```

## 使用方式
預設已設定目標頁面：
`https://tixcraft.com/activity/detail/26_dxs`

### 單次檢查
```bash
python monitor_tixcraft.py --once
```

### 持續監控（每 30 秒）
```bash
python monitor_tixcraft.py --interval 30
```

### 加上 Discord 通知
```bash
export DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/xxxx'
python monitor_tixcraft.py --interval 20
```

## 注意
- 建議自己調整 `looks_available` 裡的關鍵字，降低誤判。
- 網站內容可能由前端動態渲染，必要時可改為瀏覽器自動化方案（例如 Playwright）。
- 請遵守網站使用條款與當地法律。
