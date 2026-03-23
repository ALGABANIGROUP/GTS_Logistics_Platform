from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.database.base import Base


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class NormalBalance(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class AccountingInvoiceStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    PAID = "paid"
    CANCELLED = "cancelled"


class ExpenseInvoiceStatus(str, Enum):
    PENDING = "pending"
    POSTED = "posted"
    PAID = "paid"


class FinancialReportType(str, Enum):
    TRIAL_BALANCE = "trial_balance"
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("account_code", name="uq_accounts_account_code"),
        Index("ix_accounts_account_code", "account_code"),
        Index("ix_accounts_account_type", "account_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    account_code = Column(String(20), nullable=False, unique=True)
    account_name = Column(String(200), nullable=False)
    account_type = Column(SQLEnum(AccountType), nullable=False)
    parent_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    level = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)
    normal_balance = Column(SQLEnum(NormalBalance), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    parent = relationship("Account", remote_side=[id], backref="children")
    journal_lines = relationship("JournalEntryLine", back_populates="account")
    balances = relationship("AccountBalance", back_populates="account")


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    __table_args__ = (
        UniqueConstraint("entry_number", name="uq_journal_entries_entry_number"),
        Index("ix_journal_entries_entry_date", "entry_date"),
        Index("ix_journal_entries_reference", "reference_type", "reference_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    entry_number = Column(String(50), nullable=False, unique=True)
    entry_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(String(100), nullable=True)
    posted_by = Column(String(100), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    is_posted = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    lines = relationship("JournalEntryLine", back_populates="entry", cascade="all, delete-orphan")


class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"
    __table_args__ = (
        Index("ix_journal_entry_lines_entry_id", "entry_id"),
        Index("ix_journal_entry_lines_account_id", "account_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    debit = Column(Float, nullable=False, default=0.0)
    credit = Column(Float, nullable=False, default=0.0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account", back_populates="journal_lines")


class AccountBalance(Base):
    __tablename__ = "account_balances"
    __table_args__ = (
        UniqueConstraint("account_id", "balance_date", name="uq_account_balances_account_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    balance_date = Column(Date, nullable=False)
    opening_balance = Column(Float, nullable=False, default=0.0)
    total_debit = Column(Float, nullable=False, default=0.0)
    total_credit = Column(Float, nullable=False, default=0.0)
    closing_balance = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    account = relationship("Account", back_populates="balances")


class AccountingInvoice(Base):
    __tablename__ = "accounting_invoices"
    __table_args__ = (
        UniqueConstraint("invoice_number", name="uq_accounting_invoices_invoice_number"),
        Index("ix_accounting_invoices_status", "status"),
        Index("ix_accounting_invoices_invoice_date", "invoice_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), nullable=False, unique=True)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    customer_id = Column(Integer, nullable=True)
    customer_name = Column(String(200), nullable=True)
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, nullable=False, default=0.0)
    net_amount = Column(Float, nullable=False)
    status = Column(SQLEnum(AccountingInvoiceStatus), nullable=False, default=AccountingInvoiceStatus.DRAFT)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    journal_entry = relationship("JournalEntry")


class ExpenseInvoice(Base):
    __tablename__ = "expense_invoices"
    __table_args__ = (
        UniqueConstraint("invoice_number", name="uq_expense_invoices_invoice_number"),
        Index("ix_expense_invoices_status", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), nullable=False, unique=True)
    invoice_date = Column(Date, nullable=False)
    supplier_name = Column(String(200), nullable=True)
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False, default=0.0)
    net_amount = Column(Float, nullable=False)
    expense_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    status = Column(SQLEnum(ExpenseInvoiceStatus), nullable=False, default=ExpenseInvoiceStatus.PENDING)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    expense_account = relationship("Account")
    journal_entry = relationship("JournalEntry")


class FinancialReport(Base):
    __tablename__ = "financial_reports"
    __table_args__ = (
        Index("ix_financial_reports_report_type", "report_type"),
        Index("ix_financial_reports_report_date", "report_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(SQLEnum(FinancialReportType), nullable=False)
    report_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    data = Column(JSON, nullable=True)
    generated_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
