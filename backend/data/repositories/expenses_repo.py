from .base_repo import BaseRepo


class ExpensesRepo(BaseRepo):
    pass
    async def insert(self, *, amount: float, description: str) -> dict:
        # Replace with real ORM; raw SQL shown for brevity
        sql = "INSERT INTO expenses(amount, description) VALUES (:amount, :description) RETURNING id, amount, description"
        res = await self.execute(sql, {"amount": amount, "description": description})
        row = res.fetchone()
        return {"id": row.id, "amount": row.amount, "description": row.description}
