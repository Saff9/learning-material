---
tags: [postgresql, nodejs, prisma, orm, typescript]
---

# Prisma ORM

Next-gen ORM with schema-first design and auto-generated type-safe client.

## Installation

```bash
npm install prisma --save-dev
npm install @prisma/client
npx prisma init
```

## Schema (prisma/schema.prisma)

```prisma
generator client {
    provider = "prisma-client-js"
}

datasource db {
    provider = "postgresql"
    url      = env("DATABASE_URL")
}

model User {
    id        Int      @id @default(autoincrement())
    email     String   @unique
    name      String?
    posts     Post[]
    createdAt DateTime @default(now())
}

model Post {
    id        Int      @id @default(autoincrement())
    title     String
    body      String?
    authorId  Int
    author    User     @relation(fields: [authorId], references: [id])
    createdAt DateTime @default(now())
}
```

## Migrations

```bash
npx prisma migrate dev --name init    # create + apply migration
npx prisma generate                   # regenerate client after schema changes
npx prisma db seed                    # run seed script
```

## Type-Safe Queries

```typescript
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

// CREATE
const user = await prisma.user.create({
    data: { email: 'alice@example.com', name: 'Alice' }
});

// READ with relations (avoids N+1 automatically)
const userWithPosts = await prisma.user.findUnique({
    where: { email: 'alice@example.com' },
    include: { posts: true }
});

// UPDATE
await prisma.user.update({
    where: { id: 1 },
    data: { name: 'Alice Updated' }
});

// DELETE
await prisma.user.delete({ where: { id: 1 } });

// Transaction
await prisma.$transaction([
    prisma.user.create({ data: { email: 'a@x.com' } }),
    prisma.post.create({ data: { title: 'Hello', authorId: 1 } })
]);
```

## Next

- [[07-Application-Integration/05-Supabase|Supabase]]
- [[07-Application-Integration/06-Connection-Pooling|Connection Pooling]]
