This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

## Project Notes — Internal Audit AI UI

- Upload & tagging dokumen → POST `/api/ingest`
- Library dokumen → GET `/api/documents`
- Chat dengan citations → POST `/api/chat`
- Generate draft audit artefak → POST `/api/agent/run`

Rute/halaman yang akan dibuat:
- `app/upload/page.tsx` — form upload (drag & drop), tags JSON textarea
- `app/library/page.tsx` — tabel dokumen + filter
- `app/chat/page.tsx` — chat box + panel citations
- `app/generate/page.tsx` — form scope/risk → tampilkan hasil draft

Styling: gunakan CSS Modules atau minimal design system; hindari tema ungu default, pilih palet tegas (contoh: slate + amber).
