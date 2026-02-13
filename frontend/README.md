# Frontend (Next.js) Plan

Milestone UI minimum:
- Upload & tagging dokumen → POST `/api/ingest`.
- Library dokumen → GET `/api/documents`.
- Chat dengan citations → POST `/api/chat`.
- Generate draft audit artefak → POST `/api/agent/run`.

Rekomendasi bootstrap:
```bash
npx create-next-app@latest frontend --ts --app --no-tailwind --use-npm --import-alias @/*
```

Komponen awal:
- `app/upload/page.tsx` — form upload (drag & drop), tags JSON textarea.
- `app/library/page.tsx` — tabel dokumen.
- `app/chat/page.tsx` — chat box + panel citations.
- `app/generate/page.tsx` — form scope/risk → tampilkan hasil draft.

Styling: gunakan CSS Modules atau simple design system; hindari purple-default, pakai palet tegas (mis. slate + amber).
