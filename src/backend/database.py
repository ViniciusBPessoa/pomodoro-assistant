import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

from src.backend.settings_manager import settings

_DEFAULT_DB = Path(__file__).resolve().parent.parent.parent / "pomodoro.db"


def _db_path() -> Path:
    d = settings.get("dir_stats")
    if d:
        p = Path(d)
        p.mkdir(parents=True, exist_ok=True)
        return p / "pomodoro.db"
    return _DEFAULT_DB


def inicializar() -> None:
    with sqlite3.connect(_db_path()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ciclos (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                fase         TEXT    NOT NULL,
                duracao_min  INTEGER NOT NULL,
                duracao_seg  INTEGER NOT NULL DEFAULT 0,
                concluido    INTEGER NOT NULL DEFAULT 1,
                concluido_em TEXT    NOT NULL
            )
        """)
        # Migração: adiciona colunas novas se tabela já existia
        for col, defn in [
            ("duracao_seg", "INTEGER NOT NULL DEFAULT 0"),
            ("concluido",   "INTEGER NOT NULL DEFAULT 1"),
        ]:
            try:
                conn.execute(f"ALTER TABLE ciclos ADD COLUMN {col} {defn}")
            except sqlite3.OperationalError:
                pass


def registrar_ciclo(
    fase: str,
    duracao_min: int,
    duracao_seg: int = 0,
    concluido: bool = True,
) -> None:
    with sqlite3.connect(_db_path()) as conn:
        conn.execute(
            "INSERT INTO ciclos (fase, duracao_min, duracao_seg, concluido, concluido_em) "
            "VALUES (?, ?, ?, ?, ?)",
            (fase, duracao_min, duracao_seg, int(concluido), datetime.now().isoformat()),
        )


def buscar_ciclos(limite: int = 100) -> list[dict]:
    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM ciclos ORDER BY concluido_em DESC LIMIT ?", (limite,)
        ).fetchall()
    return [dict(row) for row in rows]


def buscar_segundos_por_dia(ano: int, mes: int) -> dict[str, int]:
    """Retorna {data_iso: segundos_de_foco} para o mês/ano solicitado."""
    inicio = f"{ano:04d}-{mes:02d}-01"
    fim_mes = 1 if mes == 12 else mes + 1
    fim_ano = ano + 1 if mes == 12 else ano
    fim = f"{fim_ano:04d}-{fim_mes:02d}-01"

    with sqlite3.connect(_db_path()) as conn:
        rows = conn.execute(
            """
            SELECT date(concluido_em) AS dia, SUM(duracao_seg) AS total_seg
            FROM ciclos
            WHERE fase = 'foco'
              AND concluido_em >= ? AND concluido_em < ?
            GROUP BY dia
            """,
            (inicio, fim),
        ).fetchall()
    return {row[0]: row[1] for row in rows}


def buscar_segundos_por_hora(data_iso: str) -> dict[int, int]:
    """Retorna {hora: segundos_de_foco} para um dia específico."""
    with sqlite3.connect(_db_path()) as conn:
        rows = conn.execute(
            """
            SELECT CAST(strftime('%H', concluido_em) AS INTEGER) AS hora,
                   SUM(duracao_seg) AS total_seg
            FROM ciclos
            WHERE fase = 'foco'
              AND date(concluido_em) = ?
            GROUP BY hora
            """,
            (data_iso,),
        ).fetchall()
    return {int(row[0]): int(row[1]) for row in rows}


def buscar_segundos_por_dia_range(inicio_iso: str, fim_iso: str) -> dict[str, int]:
    """Retorna {date_iso: segundos_de_foco} para o intervalo [inicio, fim] inclusive."""
    with sqlite3.connect(_db_path()) as conn:
        rows = conn.execute(
            """
            SELECT date(concluido_em) AS dia, SUM(duracao_seg) AS total_seg
            FROM ciclos
            WHERE fase = 'foco'
              AND date(concluido_em) BETWEEN ? AND ?
            GROUP BY dia
            """,
            (inicio_iso, fim_iso),
        ).fetchall()
    return {row[0]: int(row[1]) for row in rows}


def buscar_media_horaria_global() -> dict[int, float]:
    """Retorna {hora: média_de_segundos_por_dia} com base em todo o histórico."""
    with sqlite3.connect(_db_path()) as conn:
        n_dias = conn.execute(
            "SELECT COUNT(DISTINCT date(concluido_em)) FROM ciclos WHERE fase = 'foco'"
        ).fetchone()[0]
        if n_dias == 0:
            return {}
        rows = conn.execute(
            """
            SELECT CAST(strftime('%H', concluido_em) AS INTEGER) AS hora,
                   SUM(duracao_seg) AS total_seg
            FROM ciclos
            WHERE fase = 'foco'
            GROUP BY hora
            """,
        ).fetchall()
    return {int(row[0]): row[1] / n_dias for row in rows}


def zerar_estatisticas() -> None:
    """Remove todos os registros de ciclos. Configurações não são afetadas."""
    with sqlite3.connect(_db_path()) as conn:
        conn.execute("DELETE FROM ciclos")


def buscar_estatisticas() -> dict:
    """Retorna métricas agregadas para o dashboard."""
    with sqlite3.connect(_db_path()) as conn:
        total_focos = conn.execute(
            "SELECT COUNT(*) FROM ciclos WHERE fase = 'foco' AND concluido = 1"
        ).fetchone()[0]

        total_seg = conn.execute(
            "SELECT COALESCE(SUM(duracao_seg), 0) FROM ciclos WHERE fase = 'foco'"
        ).fetchone()[0]

        dias_rows = conn.execute(
            "SELECT DISTINCT date(concluido_em) AS dia FROM ciclos "
            "WHERE fase = 'foco' ORDER BY dia DESC"
        ).fetchall()

        streak = 0
        hoje = date.today()
        for i, (dia_str,) in enumerate(dias_rows):
            if date.fromisoformat(dia_str) == hoje - timedelta(days=i):
                streak += 1
            else:
                break

        melhor_row = conn.execute(
            """
            SELECT strftime('%w', concluido_em) AS dow, SUM(duracao_seg) AS total
            FROM ciclos WHERE fase = 'foco'
            GROUP BY dow ORDER BY total DESC LIMIT 1
            """
        ).fetchone()
        melhor_dia_semana = int(melhor_row[0]) if melhor_row else None

        seg_hoje = conn.execute(
            "SELECT COALESCE(SUM(duracao_seg), 0) FROM ciclos "
            "WHERE fase = 'foco' AND date(concluido_em) = ?",
            (hoje.isoformat(),),
        ).fetchone()[0]

    return {
        "total_focos":      total_focos,
        "total_seg":        total_seg,
        "streak_dias":      streak,
        "melhor_dia_semana": melhor_dia_semana,
        "seg_hoje":         seg_hoje,
    }
