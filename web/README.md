# web

GoEye dashboard (Next.js + React + TypeScript).

```
src/
├── app/                 # Next.js routes only (thin pages)
│   ├── layout.tsx       #   root HTML + global styles
│   ├── login/page.tsx   #   /login
│   └── (dashboard)/     #   signed-in area: top bar + login guard
│       └── page.tsx     #   /  (dashboard)
├── core/                # API client (ApiResponse envelope), login token, config, polling hook
├── components/          # shared UI: Card, StatTile, StatusBadge
└── modules/             # one folder per feature: api.ts + components/pages
    ├── auth/            #   login page, RequireAuth guard
    ├── cameras/         #   live camera tiles
    ├── dashboard/       #   dashboard page
    └── events/          #   recent events
```

Run: copy `.env.example` to `.env`, then `npm install` and `npm run dev` (http://localhost:5173).
