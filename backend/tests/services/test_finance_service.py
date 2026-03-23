# import pytest
# from backend.schemas.expense import ExpenseCreate
# from backend.services.finance_service import FinanceService

# @pytest.mark.asyncio
# async def test_create_expense_happy_path():
#     svc = FinanceService()
#     out = await svc.create_expense(ExpenseCreate(amount=10.5, description="fuel"))
#     assert out.amount == 10.5
#     assert out.description == "fuel"
#     assert isinstance(out.id, int)
# @pytest.mark.asyncio
# async def test_create_expense_invalid_amount():
#     svc = FinanceService()
#     try:
#         await svc.create_expense(ExpenseCreate(amount=-5.0, description="invalid"))
#     except ValueError as e:
#         assert str(e) == "Amount must be positive"
#     else:
#         assert False, "Expected ValueError for negative amount"
# @pytest.mark.asyncio
# async def test_create_expense_empty_description():
#     svc = FinanceService()
#     try:
#         await svc.create_expense(ExpenseCreate(amount=15.0, description=""))
#     except ValueError as e:
#         assert str(e) == "Description cannot be empty"
#     else:
#         assert False, "Expected ValueError for empty description"