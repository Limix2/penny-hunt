"use client";
import { useEffect, useState } from "react";

// Device-local notes (no login required). The backend also exposes authenticated
// per-user notes at /stores/{id}/notes for when auth is wired into the UI.
interface Note { id: number; text: string; ts: string; }

export function NotesPanel({ storeId }: { storeId: number }) {
  const key = `ph-notes-${storeId}`;
  const [notes, setNotes] = useState<Note[]>([]);
  const [text, setText] = useState("");

  useEffect(() => {
    try { setNotes(JSON.parse(localStorage.getItem(key) || "[]")); } catch {}
  }, [key]);

  const save = (next: Note[]) => { setNotes(next); localStorage.setItem(key, JSON.stringify(next)); };
  const add = () => {
    if (!text.trim()) return;
    save([{ id: Date.now(), text: text.trim(), ts: new Date().toISOString() }, ...notes]);
    setText("");
  };
  const remove = (id: number) => save(notes.filter((n) => n.id !== id));

  return (
    <section>
      <h2 className="font-semibold mb-2">My notes</h2>
      <div className="flex gap-2 mb-2">
        <input value={text} onChange={(e) => setText(e.target.value)}
          placeholder="e.g. penny aisle is endcap by registers"
          className="flex-1 border border-slate-300 rounded px-2 py-1 text-sm" />
        <button onClick={add} className="bg-slate-900 text-white text-sm px-3 rounded">Add</button>
      </div>
      <ul className="space-y-1">
        {notes.map((n) => (
          <li key={n.id} className="flex justify-between gap-2 text-sm border-t border-slate-100 py-1">
            <span>{n.text}</span>
            <button onClick={() => remove(n.id)} className="text-slate-400">✕</button>
          </li>
        ))}
        {notes.length === 0 && <li className="text-sm text-slate-400">No notes yet.</li>}
      </ul>
    </section>
  );
}
