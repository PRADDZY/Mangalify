# Mangalify Internal API

Everything you need to know about the internals.

## 🤖 Commands

| Command | Args | Who? | What it does |
|:---|:---|:---|:---|
| `/birthday set` | `dd`, `mm`, `yyyy` | User | Register your birthday. |
| `/birthday list` | - | Staff | See upcoming birthdays. |
| `/birthday export` | - | Staff | Dump DB to JSON. |
| `/holiday_post` | `name` | Staff | Manual wish trigger. |

## 💾 Database (MongoDB)

**Collections:**
- `birthdays`: `{_id: user_id, day: int, month: int, year: int}`
- `birthday_role_log`: Tracks who got the role today.
- `scheduler_meta`: Remember which holidays we've already celebrated.

## 🔌 External APIs

- **Discord**: Used for everything (Messages, Embeds, Roles).
- **AbstractAPI**: Validates dates & holidays (rate limited to 1 call/sec).
- **Tenor**: Fetches random anime GIFs for wishes.
