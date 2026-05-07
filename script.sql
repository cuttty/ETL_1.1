-- Схема DS
CREATE SCHEMA IF NOT EXISTS ds;

-- MD_ACCOUNT_D
CREATE TABLE IF NOT EXISTS ds.md_account_d (
    account_rk           BIGINT NOT NULL,
    account_number       VARCHAR(20),
    char_type            VARCHAR(10),
    currency_rk          BIGINT,
    data_actual_date     DATE NOT NULL,
    data_actual_end_date DATE,
    PRIMARY KEY (data_actual_date, account_rk)
);

-- MD_CURRENCY_D
CREATE TABLE IF NOT EXISTS ds.md_currency_d (
    currency_rk          BIGINT NOT NULL,
    currency_code        VARCHAR(3),
    currency_name        VARCHAR(100),
    data_actual_date     DATE NOT NULL,
    data_actual_end_date DATE,
    PRIMARY KEY (currency_rk, data_actual_date)
);

-- MD_EXCHANGE_RATE_D
CREATE TABLE IF NOT EXISTS ds.md_exchange_rate_d (
    currency_rk          BIGINT NOT NULL,
    rate                 NUMERIC(18,6),
    data_actual_date     DATE NOT NULL,
    data_actual_end_date DATE,
    PRIMARY KEY (data_actual_date, currency_rk)
);

-- MD_LEDGER_ACCOUNT_S
CREATE TABLE IF NOT EXISTS ds.md_ledger_account_s (
    ledger_account       VARCHAR(5) NOT NULL,
    char_type            VARCHAR(10),
    start_date           DATE NOT NULL,
    end_date             DATE,
    chapter              VARCHAR(10),
    section              VARCHAR(10),
    subsection           VARCHAR(10),
    PRIMARY KEY (ledger_account, start_date)
);

-- FT_POSTING_F
CREATE TABLE IF NOT EXISTS ds.ft_posting_f (
    oper_date            DATE,
    account_debit        VARCHAR(20),
    account_credit       VARCHAR(20),
    amount               NUMERIC(18,2),
);

-- FT_BALANCE_F
CREATE TABLE IF NOT EXISTS ds.ft_balance_f (
    on_date              DATE NOT NULL,
    account_rk           BIGINT NOT NULL,
    balance_out          NUMERIC(18,2),
    balance_out_rub      NUMERIC(18,2),
    PRIMARY KEY (on_date, account_rk)
);

-- Схема логов
CREATE SCHEMA IF NOT EXISTS logs;
-- Таблица для логов 
CREATE TABLE IF NOT EXISTS logs.etl_log (
    log_id         SERIAL PRIMARY KEY,
    process_name   TEXT,
    start_time     TIMESTAMP,
    end_time       TIMESTAMP,
    status         TEXT,
    rows_processed INT,
    message        TEXT
);