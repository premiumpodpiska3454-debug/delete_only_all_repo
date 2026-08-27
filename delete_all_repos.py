import requests
import getpass
import sys


# ============================================================
# ЗАПРОС ТОКЕНА
# ============================================================

print("=" * 70)
print("🗑️ УДАЛЕНИЕ GITHUB РЕПОЗИТОРИЕВ")
print("=" * 70)

TOKEN = getpass.getpass(
    "🔑 Введи GitHub Token: "
).strip()

if not TOKEN:
    print("❌ Токен не введён.")
    sys.exit(1)


# ============================================================
# GITHUB API
# ============================================================

BASE_URL = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2026-03-10",
}

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# ПРОВЕРКА ТОКЕНА
# ============================================================

print("\n🔎 Проверяю токен...")

try:

    response = session.get(
        f"{BASE_URL}/user",
        timeout=15
    )

except Exception as e:

    print(f"❌ Ошибка соединения: {e}")
    sys.exit(1)


if response.status_code != 200:

    print(
        f"❌ Токен не работает. "
        f"HTTP {response.status_code}"
    )

    try:
        print(
            response.json().get(
                "message",
                response.text
            )
        )
    except Exception:
        print(response.text)

    sys.exit(1)


user = response.json()

login = user.get("login")

print(f"✅ Авторизация успешна: {login}")


# ============================================================
# ПОЛУЧЕНИЕ ВСЕХ РЕПОЗИТОРИЕВ
# ============================================================

print("\n🔎 Получаю список репозиториев...")

repos = []

page = 1

while True:

    try:

        response = session.get(
            f"{BASE_URL}/user/repos",
            params={
                "per_page": 100,
                "page": page,
                "affiliation": "owner",
            },
            timeout=15
        )

    except Exception as e:

        print(f"❌ Ошибка соединения: {e}")
        sys.exit(1)

    if response.status_code != 200:

        print(
            f"❌ Ошибка получения репозиториев: "
            f"HTTP {response.status_code}"
        )

        try:
            print(
                response.json().get(
                    "message",
                    response.text
                )
            )
        except Exception:
            print(response.text)

        sys.exit(1)

    data = response.json()

    if not isinstance(data, list):

        print("❌ GitHub вернул неожиданный ответ:")
        print(data)

        sys.exit(1)

    if not data:
        break

    repos.extend(data)

    if len(data) < 100:
        break

    page += 1


# ============================================================
# ЕСЛИ НЕТ РЕПОЗИТОРИЕВ
# ============================================================

if not repos:

    print("\n✅ Репозиториев не найдено.")
    sys.exit(0)


# ============================================================
# ПОКАЗЫВАЕМ СПИСОК
# ============================================================

print()
print("=" * 70)
print("📋 НАЙДЕННЫЕ РЕПОЗИТОРИИ")
print("=" * 70)

for number, repo in enumerate(repos, 1):

    print(
        f"{number:3d}. {repo['full_name']}"
    )

print("=" * 70)

print(
    f"📊 Всего найдено: {len(repos)}"
)


# ============================================================
# ПОДТВЕРЖДЕНИЕ
# ============================================================

print()
print(
    "⚠️ ВНИМАНИЕ!"
)

print(
    "Удаление репозиториев необратимо."
)

print()

confirm = input(
    'Для удаления ВСЕХ этих репозиториев введи DELETE: '
).strip()


if confirm != "DELETE":

    print(
        "\n⛔ Отменено. Ничего не удалено."
    )

    sys.exit(0)


# ============================================================
# УДАЛЕНИЕ
# ============================================================

print()
print("=" * 70)
print("🗑️ НАЧИНАЮ УДАЛЕНИЕ")
print("=" * 70)

deleted = 0
failed = 0


for number, repo in enumerate(
    repos,
    1
):

    full_name = repo["full_name"]

    print(
        f"[{number}/{len(repos)}] "
        f"🗑️ {full_name} ... ",
        end="",
        flush=True
    )

    try:

        response = session.delete(
            f"{BASE_URL}/repos/{full_name}",
            timeout=20
        )

    except Exception as e:

        print("❌")
        print(f"    Ошибка: {e}")

        failed += 1
        continue


    if response.status_code == 204:

        print("✅")

        deleted += 1

    else:

        print(
            f"❌ HTTP {response.status_code}"
        )

        try:

            error = response.json()

            print(
                f"    {error.get('message', error)}"
            )

        except Exception:

            print(
                f"    {response.text}"
            )

        failed += 1


# ============================================================
# ИТОГ
# ============================================================

print()
print("=" * 70)
print("🏁 ГОТОВО")
print("=" * 70)

print(
    f"📊 Всего найдено: {len(repos)}"
)

print(
    f"✅ Удалено: {deleted}"
)

print(
    f"❌ Ошибок: {failed}"
)

print("=" * 70)
