from sqlalchemy import Column, create_engine, ForeignKey, FetchedValue, Integer
from sqlalchemy.dialects import mssql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


class BatchLog(Base):
    __tablename__ = 'BatchLog'
    __table_args__ = {'schema': 'aud'}

    BatchLogID = Column('BatchLogID', mssql.INTEGER, nullable=False, primary_key=True)
    Start = Column('Start', mssql.DATETIME, nullable=False)
    End = Column('End', mssql.DATETIME, nullable=True)
    IsSuccessful = Column('IsSuccessful', mssql.BIT, nullable=False)


class TableRefreshLog(Base):
    __tablename__ = 'TableRefreshLog'
    __table_args__ = {'schema': 'aud'}
    BatchLog = relationship('BatchLog')

    TableRefreshLogID = Column('TableRefreshLogID', mssql.INTEGER, nullable=False, primary_key=True)
    BatchLogID = Column('BatchLogID', mssql.INTEGER, ForeignKey('aud.BatchLog.BatchLogID'), nullable=False)
    ItemName = Column('ItemName', mssql.VARCHAR(50), nullable=False)
    Start = Column('Start', mssql.DATETIME, nullable=False)
    End = Column('End', mssql.DATETIME, nullable=True)
    IsSuccessful = Column('IsSuccessful', mssql.BIT, nullable=False)


class AccessToken(Base):
    __tablename__ = 'AccessToken'
    __table_args__ = {'schema': 'dbo'}
    Institution = relationship('Institution')

    AccessToken = Column('AccessToken', mssql.VARCHAR(51), nullable=False, primary_key=True)
    ItemID = Column('ItemID', mssql.VARCHAR(37), nullable=False)
    Environment = Column('Environment', mssql.VARCHAR(10), nullable=False)
    InstitutionID = Column('InstitutionID', mssql.VARCHAR(10), ForeignKey('dbo.Institution.InstitutionID'), nullable=False)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)


class Account(Base):
    __tablename__ = 'Account'
    __table_args__ = {'schema': 'dbo'}
    AccessToken = relationship('AccessToken')

    AccountID = Column('AccountID', mssql.VARCHAR(37), nullable=False, primary_key=True)
    AccessToken = Column('AccessToken', mssql.VARCHAR(51), ForeignKey('dbo.AccessToken.AccessToken'), nullable=False)
    Mask = Column('Mask', mssql.INTEGER, nullable=True)
    Name = Column('Name', mssql.VARCHAR(100), nullable=False)
    OfficialName = Column('OfficialName', mssql.VARCHAR(100), nullable=True)
    AccountType = Column('AccountType', mssql.VARCHAR(50), nullable=False)
    AccountSubType = Column('AccountSubType', mssql.VARCHAR(50), nullable=False)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)


class Balance(Base):
    __tablename__ = 'Balance'
    __table_args__ = {'schema': 'dbo'}
    Account = relationship('Account')

    AccountID = Column('AccountID', mssql.VARCHAR(37), ForeignKey('dbo.Account.AccountID'), nullable=False, primary_key=True, autoincrement=False)
    CurrentBalance = Column('CurrentBalance', mssql.DECIMAL(13,2), nullable=False)
    AvailableBalance = Column('AvailableBalance', mssql.DECIMAL(13,2), nullable=True)
    BalanceLimit = Column('BalanceLimit', mssql.DECIMAL(13,2), nullable=True)
    ISOCurrencyCode = Column('ISOCurrencyCode', mssql.VARCHAR(25), nullable=True)
    UnofficialCurrencyCode = Column('UnofficialCurrencyCode', mssql.VARCHAR(25), nullable=True)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)


class Category(Base):
    __tablename__ = 'Category'
    __table_args__ = {'schema': 'dbo'}

    CategoryID = Column('CategoryID', mssql.INTEGER, nullable=False, primary_key=True, autoincrement=False)
    CategoryGroup = Column('CategoryGroup', mssql.VARCHAR(25), nullable=False)
    CategoryHierarchy1 = Column('CategoryHierarchy1', mssql.VARCHAR(50), nullable=False)
    CategoryHierarchy2 = Column('CategoryHierarchy2', mssql.VARCHAR(50), nullable=True)
    CategoryHierarchy3 = Column('CategoryHierarchy3', mssql.VARCHAR(50), nullable=True)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)


class Institution(Base):
    __tablename__ = 'Institution'
    __table_args__ = {'schema': 'dbo'}

    InstitutionID = Column('InstitutionID', mssql.VARCHAR(10), nullable=False, primary_key=True)
    InstitutionName = Column('InstitutionName', mssql.VARCHAR(100), nullable=False)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)


class InvestmentHolding(Base):
    __tablename__ = 'InvestmentHolding'
    __table_args__ = {'schema': 'dbo'}
    Account = relationship('Account')
    InvestmentSecurity = relationship('InvestmentSecurity')

    AccountID = Column('AccountID', mssql.VARCHAR(37), ForeignKey('dbo.Account.AccountID'), nullable=False, primary_key=True, autoincrement=False)
    InvestmentSecurityID = Column('InvestmentSecurityID', mssql.VARCHAR(37), ForeignKey('dbo.InvestmentSecurity.InvestmentSecurityID'), nullable=False, primary_key=True)
    InstitutionPrice = Column('InstitutionPrice', mssql.FLOAT, nullable=False)
    InstitutionPriceAsOf = Column('InstitutionPriceAsOf', mssql.DATETIME, nullable=True)
    InstitutionValue = Column('InstitutionValue', mssql.FLOAT, nullable=False)
    CostBasis = Column('CostBasis', mssql.FLOAT, nullable=True)
    Quantity = Column('Quantity', mssql.FLOAT, nullable=False)
    ISOCurrencyCode = Column('ISOCurrencyCode', mssql.VARCHAR(25), nullable=True)
    UnofficialCurrencyCode = Column('UnofficialCurrencyCode', mssql.VARCHAR(25), nullable=True)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)


class InvestmentSecurity(Base):
    __tablename__ = 'InvestmentSecurity'
    __table_args__ = {'schema': 'dbo'}
    Institution = relationship('Institution')

    InvestmentSecurityID = Column('InvestmentSecurityID', mssql.VARCHAR(37), nullable=False, primary_key=True, autoincrement=False)
    InstitutionID = Column('InstitutionID', mssql.VARCHAR(10), ForeignKey('dbo.Institution.InstitutionID'), nullable=True)
    ISIN = Column('ISIN', mssql.VARCHAR(12), nullable=True)
    CUSIP = Column('CUSIP', mssql.VARCHAR(9), nullable=True)
    SEDOL = Column('SEDOL', mssql.VARCHAR(7), nullable=True)
    InstitutionSecurityID = Column('InstitutionSecurityID', mssql.VARCHAR(37), nullable=True)
    ProxyInvestmentSecurityID = Column('ProxyInvestmentSecurityID', mssql.VARCHAR(37), nullable=True)
    Name = Column('Name', mssql.VARCHAR(100), nullable=True)
    TickerSymbol = Column('TickerSymbol', mssql.VARCHAR(50), nullable=True)
    IsCashEquivalent = Column('IsCashEquivalent', mssql.BIT, nullable=False)
    Type = Column('Type', mssql.VARCHAR(50), nullable=False)
    ClosePrice = Column('ClosePrice', mssql.FLOAT, nullable=True)
    ClosePriceAsOf = Column('ClosePriceAsOf', mssql.DATETIME, nullable=True)
    ISOCurrencyCode = Column('ISOCurrencyCode', mssql.VARCHAR(25), nullable=True)
    UnofficialCurrencyCode = Column('UnofficialCurrencyCode', mssql.VARCHAR(25), nullable=True)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)


class InvestmentTransaction(Base):
    __tablename__ = 'InvestmentTransaction'
    __table_args__ = {'schema': 'dbo'}
    Account = relationship('Account')
    InvestmentSecurity = relationship('InvestmentSecurity')

    InvestmentTransactionID = Column('InvestmentTransactionID', mssql.VARCHAR(37), nullable=False, primary_key=True, autoincrement=False)
    AccountID = Column('AccountID', mssql.VARCHAR(37), ForeignKey('dbo.Account.AccountID'), nullable=False)
    InvestmentSecurityID = Column('InvestmentSecurityID', mssql.VARCHAR(37), ForeignKey('dbo.InvestmentSecurity.InvestmentSecurityID'), nullable=True)
    Date = Column('Date', mssql.DATETIME, nullable=False)
    Name = Column('Name', mssql.VARCHAR(100), nullable=False)
    Quantity = Column('Quantity', mssql.FLOAT, nullable=False)
    Amount = Column('Amount', mssql.FLOAT, nullable=False)
    Price = Column('Price', mssql.FLOAT, nullable=False)
    Fees = Column('Fees', mssql.FLOAT, nullable=True)
    Type = Column('Type', mssql.VARCHAR(50), nullable=False)
    SubType = Column('SubType', mssql.VARCHAR(50), nullable=False)
    ISOCurrencyCode = Column('ISOCurrencyCode', mssql.VARCHAR(25), nullable=True)
    UnofficialCurrencyCode = Column('UnofficialCurrencyCode', mssql.VARCHAR(25), nullable=True)
    CancelTransactionID = Column('CancelTransactionID', mssql.VARCHAR(100), nullable=True)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)


class LiabilityCreditCard(Base):
    __tablename__ = 'LiabilityCreditCard'
    __table_args__ = {'schema': 'dbo'}
    Account = relationship('Account')

    AccountID = Column('AccountID', mssql.VARCHAR(37), ForeignKey('dbo.Account.AccountID'), nullable=False, primary_key=True, autoincrement=False)
    APRPercentage = Column('APRPercentage', mssql.FLOAT, nullable=True)
    APRType = Column('APRType', mssql.VARCHAR(25), nullable=True)
    BalanceSubjectToAPR = Column('BalanceSubjectToAPR', mssql.DECIMAL(13,2), nullable=True)
    InterestChargeAmount = Column('InterestChargeAmount', mssql.DECIMAL(13,2), nullable=True)
    IsOverdue = Column('IsOverdue', mssql.BIT, nullable=True)
    LastPaymentAmount = Column('LastPaymentAmount', mssql.DECIMAL(13,2), nullable=True)
    LastPaymentDate = Column('LastPaymentDate', mssql.DATETIME, nullable=True)
    LastStatementBalance = Column('LastStatementBalance', mssql.FLOAT, nullable=True)
    LastStatementIssueDate = Column('LastStatementIssueDate', mssql.DATETIME, nullable=True)
    MinimumPaymentAmount = Column('MinimumPaymentAmount', mssql.FLOAT, nullable=True)
    NextPaymentDueDate = Column('NextPaymentDueDate', mssql.DATETIME, nullable=True)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)


class LiabilityMortgage(Base):
    __tablename__ = 'LiabilityMortgage'
    __table_args__ = {'schema': 'dbo'}
    Account = relationship('Account')

    AccountID = Column('AccountID', mssql.VARCHAR(37), ForeignKey('dbo.Account.AccountID'), nullable=False, primary_key=True, autoincrement=False)
    AccountNumber = Column('AccountNumber', mssql.BIGINT, nullable=True)
    CurrentLateFee = Column('CurrentLateFee', mssql.DECIMAL(13,2), nullable=True)
    EscrowBalance = Column('EscrowBalance', mssql.DECIMAL(13,2), nullable=True)
    HasPMI = Column('HasPMI', mssql.BIT, nullable=True)
    HasPrepaymentPenalty = Column('HasPrepaymentPenalty', mssql.BIT, nullable=True)
    InterestRate = Column('InterestRate', mssql.FLOAT, nullable=True)
    InterestRateType = Column('InterestRateType', mssql.VARCHAR(50), nullable=True)
    LastPaymentAmount = Column('LastPaymentAmount', mssql.DECIMAL(13,2), nullable=True)
    LastPaymentDate = Column('LastPaymentDate', mssql.DATETIME, nullable=True)
    LoanTerm = Column('LoanTerm', mssql.VARCHAR(100), nullable=True)
    LoanTypeDescription = Column('LoanTypeDescription', mssql.VARCHAR(50), nullable=True)
    MaturityDate = Column('MaturityDate', mssql.DATETIME, nullable=True)
    NextMonthlyPayment = Column('NextMonthlyPayment', mssql.DECIMAL(13,2), nullable=True)
    NextPaymentDueDate = Column('NextPaymentDueDate', mssql.DATETIME, nullable=True)
    OriginationDate = Column('OriginationDate', mssql.DATETIME, nullable=True)
    OriginationPrincipalAmount = Column('OriginationPrincipalAmount', mssql.DECIMAL(13,2), nullable=True)
    PastDueAmount = Column('PastDueAmount', mssql.DECIMAL(13,2), nullable=True)
    PropertyStreet = Column('PropertyStreet', mssql.VARCHAR(100), nullable=True)
    PropertyCity = Column('PropertyCity', mssql.VARCHAR(100), nullable=True)
    PropertyRegion = Column('PropertyRegion', mssql.VARCHAR(100), nullable=True)
    PropertyCountry = Column('PropertyCountry', mssql.VARCHAR(100), nullable=True)
    PropertyPostalCode = Column('PropertyPostalCode', mssql.VARCHAR(100), nullable=True)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)


class LiabilityStudentLoan(Base):
    __tablename__ = 'LiabilityStudentLoan'
    __table_args_ = {'schema': 'dbo'}
    Account = relationship('Account')

    AccountID = Column('AccountID', mssql.VARCHAR(37), ForeignKey('dbo.Account.AccountID'), nullable=True, primary_key=True, autoincrement=False)
    AccountNumber = Column('AccountNumber', mssql.BIGINT, nullable=True)
    DisbursementDates = Column('DisbursementDates', mssql.VARCHAR(max), nullable=True)
    ExpectedPayoffDate = Column('ExpectedPayoffDate', mssql.DATETIME, nullable=True)
    Guarantor = Column('Guarantor', mssql.VARCHAR(100), nullable=True)
    InterestRatePercentage = Column('InterestRatePercentage', mssql.FLOAT, nullable=False)
    IsOverdue = Column('IsOverdue', mssql.BIT, nullable=True)
    LastPaymentAmount = Column('LastPaymentAmount', mssql.DECIMAL(13,2), nullable=True)
    LastStatementBalance = Column('LastStatementBalance', mssql.FLOAT, nullable=True)
    LastStatementIssueDate = Column('LastStatementIssueDate', mssql.DATETIME, nullable=True)
    LoanName = Column('LoanName', mssql.VARCHAR(100), nullable=True)
    LoanStatusType = Column('LoanStatusType', mssql.VARCHAR(100), nullable=True)
    LoanStatusEndDate = Column('LoanStatusEndDate', mssql.DATETIME, nullable=True)
    MinimumPaymentAmount = Column('MinimumPaymentAmount', mssql.FLOAT, nullable=True)
    NextPaymentDueDate = Column('NextPaymentDueDate', mssql.DATETIME, nullable=True)
    OriginationDate = Column('OriginationDate', mssql.DATETIME, nullable=True)
    OriginationPrincipalAmount = Column('OriginationPrincipalAmount', mssql.FLOAT, nullable=True)
    OutstandingInterestAmount = Column('OutstandingInterestAmount', mssql.FLOAT, nullable=True)
    PaymentReferenceNumber = Column('PaymentReferenceNumber', mssql.VARCHAR(100), nullable=True)
    PSLFEstimatedEligibilityDate = Column('PSLFEstimatedEligibilityDate', mssql.DATETIME, nullable=True)
    PSLFPaymentsMade = Column('PSLFPaymentsMade', mssql.INTEGER, nullable=True)
    PSLFPaymentsRemaining = Column('PSLFPaymentsRemaining', mssql.INTEGER, nullable=True)
    RepaymentPlanType = Column('RepaymentPlanType', mssql.VARCHAR(100), nullable=True)
    RepaymentPlanDescription = Column('RepaymentPlanDescription', mssql.VARCHAR(100), nullable=True)
    SequenceNumber = Column('SequenceNumber', mssql.VARCHAR(100), nullable=True)
    ServicerStreet = Column('ServicerStreet', mssql.VARCHAR(100), nullable=True)
    ServicerCity = Column('ServicerCity', mssql.VARCHAR(100), nullable=True)
    ServicerRegion = Column('ServicerRegion', mssql.VARCHAR(50), nullable=True)
    ServicerPostalCode = Column('ServicerPostalCode', mssql.VARCHAR(10), nullable=True)
    ServicerCountry = Column('ServicerCountry', mssql.VARCHAR(50), nullable=True)
    YTDInterestPaid = Column('YTDInterestPaid', mssql.FLOAT, nullable=True)
    YTDPrincipalPaid = Column('YTDPrincipalPaid', mssql.FLOAT, nullable=True)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)


class Transaction(Base):
    __tablename__ = 'Transaction'
    __table_args__ = {'schema': 'dbo'}
    Account = relationship('Account')
    Category = relationship('Category')

    TransactionID = Column('TransactionID', mssql.VARCHAR(37), nullable=False, primary_key=True, autoincrement=False)
    AccountID = Column('AccountID', mssql.VARCHAR(37), ForeignKey('dbo.Account.AccountID'), nullable=False)
    CategoryID = Column('CategoryID', mssql.INTEGER, ForeignKey('dbo.Category.CategoryID'), nullable=True)
    AuthorizedDate = Column('AuthorizedDate', mssql.DATETIME, nullable=True)
    Date = Column('Date', mssql.DATETIME, nullable=False)
    TransactionType = Column('TransactionType', mssql.VARCHAR(25), nullable=False)
    Name = Column('Name', mssql.VARCHAR(100), nullable=False)
    Amount = Column('Amount', mssql.DECIMAL(13,2), nullable=False)
    ISOCurrencyCode = Column('ISOCurrencyCode', mssql.VARCHAR(25), nullable=True)
    UnofficialCurrencyCode = Column('UnofficialCurrencyCode', mssql.VARCHAR(25), nullable=True)
    PaymentChannel = Column('PaymentChannel', mssql.VARCHAR(100), nullable=False)
    PendingStatus = Column('PendingStatus', mssql.BIT, nullable=False)
    PendingTransactionID = Column('PendingTransactionID', mssql.VARCHAR(37), nullable=True)
    dCreated = Column('dCreated', mssql.DATETIME, FetchedValue(), nullable=False)
    dModified = Column('dModified', mssql.DATETIME, FetchedValue(), nullable=False)

