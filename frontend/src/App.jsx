import { useEffect, useState } from "react";

const CATEGORIES = ["Food", "Travel", "Bills", "Shopping", "Other"];
const today = () => new Date().toISOString().slice(0, 10);
const emptyForm = () => ({ title: "", amount: "", category: "Food", spent_on: today() });
const money = (value) => `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;

export default function App() {
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState({ total: 0, count: 0, by_category: {} });
  const [form, setForm] = useState(emptyForm());
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    const [list, stats] = await Promise.all([fetch("/api/expenses"), fetch("/api/expenses/summary")]);
    setExpenses(await list.json());
    setSummary(await stats.json());
  }

  useEffect(() => {
    load().catch(() => setError("Could not reach the backend."));
  }, []);

  async function save(event) {
    event.preventDefault();
    const response = await fetch(editingId ? `/api/expenses/${editingId}` : "/api/expenses", {
      method: editingId ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...form, amount: Number(form.amount) }),
    });
    if (!response.ok) {
      setError("Please enter a title, an amount above 0 and a date.");
      return;
    }
    setError("");
    setForm(emptyForm());
    setEditingId(null);
    load();
  }

  function startEdit(expense) {
    setEditingId(expense.id);
    setForm({ title: expense.title, amount: expense.amount, category: expense.category, spent_on: expense.spent_on });
  }

  async function remove(id) {
    await fetch(`/api/expenses/${id}`, { method: "DELETE" });
    load();
  }

  const update = (field) => (event) => setForm({ ...form, [field]: event.target.value });

  return (
    <main className="page">
      <header>
        <h1>Expense Tracker</h1>
        <p>Track where your money goes, deployed by Argo CD.</p>
      </header>

      <section className="cards">
        <div className="card total">
          <span>Total spent</span>
          <strong>{money(summary.total)}</strong>
          <small>{summary.count} expenses</small>
        </div>
        {CATEGORIES.map((category) => (
          <div className="card" key={category}>
            <span>{category}</span>
            <strong>{money(summary.by_category[category] || 0)}</strong>
          </div>
        ))}
      </section>

      <section className="panel">
        <h2>{editingId ? "Edit expense" : "Add expense"}</h2>
        <form onSubmit={save}>
          <input placeholder="What did you spend on?" value={form.title} onChange={update("title")} required />
          <input type="number" min="0.01" step="0.01" placeholder="Amount" value={form.amount} onChange={update("amount")} required />
          <select value={form.category} onChange={update("category")}>
            {CATEGORIES.map((category) => (
              <option key={category}>{category}</option>
            ))}
          </select>
          <input type="date" value={form.spent_on} onChange={update("spent_on")} required />
          <button type="submit">{editingId ? "Save" : "Add"}</button>
          {editingId && (
            <button type="button" className="secondary" onClick={() => { setEditingId(null); setForm(emptyForm()); }}>
              Cancel
            </button>
          )}
        </form>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="panel">
        <h2>Expenses</h2>
        {expenses.length === 0 ? (
          <p className="empty">No expenses yet. Add your first one above.</p>
        ) : (
          <table>
            <thead>
              <tr><th>Date</th><th>Title</th><th>Category</th><th>Amount</th><th></th></tr>
            </thead>
            <tbody>
              {expenses.map((expense) => (
                <tr key={expense.id}>
                  <td>{expense.spent_on}</td>
                  <td>{expense.title}</td>
                  <td><span className="tag">{expense.category}</span></td>
                  <td>{money(expense.amount)}</td>
                  <td className="actions">
                    <button className="secondary" onClick={() => startEdit(expense)}>Edit</button>
                    <button className="danger" onClick={() => remove(expense.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
