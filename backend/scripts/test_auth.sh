#!/bin/bash
# ============================================================
#  DMS Auth — Ejemplos de uso con curl
#  Ejecuta desde la raíz del proyecto con el backend corriendo
# ============================================================

BASE="http://localhost:8000"

echo "═══════════════════════════════════════"
echo " 1. REGISTRO"
echo "═══════════════════════════════════════"
curl -s -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Carlos Admin",
    "email": "admin@dms.com",
    "password": "Admin1234",
    "role": "ADMIN"
  }' | python -m json.tool

echo ""
echo "═══════════════════════════════════════"
echo " 2. REGISTRO — OPERATOR"
echo "═══════════════════════════════════════"
curl -s -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Ana Operadora",
    "email": "operator@dms.com",
    "password": "Operator1234",
    "role": "OPERATOR"
  }' | python -m json.tool

echo ""
echo "═══════════════════════════════════════"
echo " 3. LOGIN — Obtener tokens"
echo "═══════════════════════════════════════"
LOGIN_RESP=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@dms.com", "password": "Admin1234"}')

echo $LOGIN_RESP | python -m json.tool

# Extraer tokens (requiere jq)
ACCESS_TOKEN=$(echo $LOGIN_RESP | python -c "import sys,json; d=json.load(sys.stdin); print(d['tokens']['access_token'])")
REFRESH_TOKEN=$(echo $LOGIN_RESP | python -c "import sys,json; d=json.load(sys.stdin); print(d['tokens']['refresh_token'])")

echo "ACCESS_TOKEN: ${ACCESS_TOKEN:0:50}..."
echo "REFRESH_TOKEN: ${REFRESH_TOKEN:0:50}..."

echo ""
echo "═══════════════════════════════════════"
echo " 4. GET /auth/me — Perfil autenticado"
echo "═══════════════════════════════════════"
curl -s -X GET "$BASE/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python -m json.tool

echo ""
echo "═══════════════════════════════════════"
echo " 5. REFRESH — Rotar tokens"
echo "═══════════════════════════════════════"
NEW_TOKENS=$(curl -s -X POST "$BASE/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")
echo $NEW_TOKENS | python -m json.tool

NEW_ACCESS=$(echo $NEW_TOKENS | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo ""
echo "═══════════════════════════════════════"
echo " 6. Ruta protegida — Solo ADMIN"
echo "═══════════════════════════════════════"
curl -s -X GET "$BASE/examples/admin-only" \
  -H "Authorization: Bearer $NEW_ACCESS" | python -m json.tool

echo ""
echo "═══════════════════════════════════════"
echo " 7. Ruta OPERATOR — Con token de ADMIN"
echo "═══════════════════════════════════════"
curl -s -X GET "$BASE/examples/operator" \
  -H "Authorization: Bearer $NEW_ACCESS" | python -m json.tool

echo ""
echo "═══════════════════════════════════════"
echo " 8. Ruta sin token — Error 401"
echo "═══════════════════════════════════════"
curl -s -X GET "$BASE/examples/authenticated" | python -m json.tool

echo ""
echo "═══════════════════════════════════════"
echo " 9. LOGIN fallido — Error 401"
echo "═══════════════════════════════════════"
curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@dms.com", "password": "wrongpassword"}' | python -m json.tool

echo ""
echo "═══════════════════════════════════════"
echo " 10. LOGOUT"
echo "═══════════════════════════════════════"
curl -s -X POST "$BASE/auth/logout" \
  -H "Authorization: Bearer $NEW_ACCESS" | python -m json.tool

echo ""
echo "✅ Pruebas completas"
