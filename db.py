import streamlit as st
from supabase import create_client

@st.cache_resource
def _client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def init_db():
    pass  # table is created once in the Supabase dashboard (SQL below)

def save_test_result(*, result_id=None, name, cnic, background,
                     holland_code, scores, answers, consent_followup=False):
    row = {
        "name": name, "cnic": cnic or None, "background": background,
        "holland_code": holland_code, "consent_followup": consent_followup,
        "scores": scores, "answers": answers,   # jsonb columns — no json.dumps needed
    }
    sb = _client()
    if result_id:
        sb.table("test_results").update(row).eq("id", result_id).execute()
        return result_id
    resp = sb.table("test_results").insert(row).execute()
    return resp.data[0]["id"]

def get_all_results(limit=500):
    resp = _client().table("test_results").select("*") \
        .order("created_at", desc=True).limit(limit).execute()
    return resp.data

def find_by_cnic(cnic):
    resp = _client().table("test_results").select("*") \
        .eq("cnic", cnic).order("created_at", desc=True).execute()
    return resp.data

def save_feedback(student_name, holland_code, message_index, rating, question, answer):
    """Persist one thumbs rating on a counsellor answer."""
    _client().table("feedback").insert({
        "student_name": student_name,
        "holland_code": holland_code,
        "message_index": message_index,
        "rating": rating,
        "question": question,
        "answer": answer,
    }).execute()