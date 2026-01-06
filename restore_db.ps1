# restore_bb_test.ps1
# ===================
# Script za Windows PowerShell
# Drop + Create + Restore PostgreSQL 18 baze bb_test

# Postavi putanju do PostgreSQL bin foldera (ako PATH nije setovan)
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"

# PostgreSQL korisnik
$PGUSER = "postgres"

# Ime baze
$DBNAME = "bb_test"

# Putanja do backup fajla (.backup) ili foldera
$BACKUP_PATH = "C:\myPython\PythonLearning\bbWeb\database_backup\bck_bb_test_20260105_1615.backup"

Write-Host "1️⃣ Prekid konekcija ka bazi..."
psql -U $PGUSER -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$DBNAME';"

Write-Host "2️⃣ Brisanje baze (dropdb)..."
dropdb -U $PGUSER $DBNAME

Write-Host "3️⃣ Kreiranje nove baze (createdb)..."
createdb -U $PGUSER $DBNAME

Write-Host "4️⃣ Restore iz backup-a..."
pg_restore -U $PGUSER -d $DBNAME $BACKUP_PATH

Write-Host "✅ Restore završen."
