# app.py
import os, pathlib, joblib
import numpy as np
import pandas as pd
import streamlit as st

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(page_title="AI 쓰나미 예측 & 대응", layout="wide")
st.title("🌊 AI로 쓰나미 예측하고, 행동으로 이어가기")

# --------------------------------------------------
# (A) 스타일 (반드시 문자열로 감싸기)
# --------------------------------------------------
st.markdown("""
<style>
  .banner{padding:14px 16px;border-radius:14px;background:linear-gradient(135deg,#1f6feb,#7c3aed);
           color:white;box-shadow:0 10px 18px rgba(0,0,0,.10);margin-bottom:12px;}
  .chip{display:inline-block;padding:6px 10px;border-radius:16px;background:rgba(255,255,255,.20);
        color:#fff;font-weight:600;margin-right:8px;font-size:.85rem;}
  .card{border-radius:16px;padding:16px;background:#fff;border:1px solid #ececec;
        box-shadow:0 8px 16px rgba(0,0,0,.06);height:100%;}
  .ok{background:#ecfdf5;border-color:#d1fae5;}
  .warn{background:#fff7ed;border-color:#ffedd5;}
  .danger{background:#fef2f2;border-color:#fee2e2;}
  .badge{display:inline-block;padding:4px 8px;border-radius:10px;font-size:.8rem;font-weight:700;color:#fff;}
  .badge-red{background:#ef4444;} .badge-amber{background:#f59e0b;} .badge-green{background:#10b981;}
  .timeline{list-style:none;padding-left:0;} .timeline li{margin:10px 0;padding-left:12px;border-left:3px solid #e5e7eb;}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# (B) 대응 카드 UI
# --------------------------------------------------
def render_safety_ui(prob: float, threshold: float = 0.5):
    st.markdown(f"""
    <div class="banner">
      <div style="font-size:1.2rem;">🌊 <b>쓰나미 대응 가이드</b></div>
      <div style="margin-top:8px;">
        <span class="chip">예측 확률: {prob*100:.1f}%</span>
        <span class="chip">판정 기준: {threshold*100:.0f}%</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if prob >= threshold:
        st.markdown('<span class="badge badge-red">위험도: 높음</span>', unsafe_allow_html=True)
        tone, lead = "danger", "🚨 발생 가능성 ‘높음’ — 즉시 대피 절차를 확인하세요."
    elif prob >= threshold * 0.6:
        st.markdown('<span class="badge badge-amber">위험도: 중간</span>', unsafe_allow_html=True)
        tone, lead = "warn", "⚠️ 주의 — 경보·방송 확인 및 대피 경로 점검이 필요합니다."
    else:
        st.markdown('<span class="badge badge-green">위험도: 낮음</span>', unsafe_allow_html=True)
        tone, lead = "ok", "✅ 낮음 — 그래도 해안 지역은 평소 대피 경로를 숙지하세요."
    st.info(lead)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="card {tone}">
          <h4>⏱️ 즉시(분 단위)</h4>
          <ul class="timeline">
            <li>해안·하천·방파제·지하차도 <b>접근 금지</b></li>
            <li><b>높은 지대</b> 또는 지정 대피소로 이동(가능하면 도보)</li>
            <li>재난문자·라디오·관공서 방송 확인</li>
            <li>1차 파도 뒤 <b>추가 파도</b> 대비</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="card {tone}">
          <h4>🧭 단기(시간 단위)</h4>
          <ul class="timeline">
            <li>가족·팀원 <b>연락/합류 지점</b> 확인</li>
            <li><b>응급키트·식수</b> 확보, 감염·저체온 대비</li>
            <li>해안 접근 금지, 2차·3차 파도 주의</li>
            <li>전기·가스·수도 밸브 잠그고 이동</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="card {tone}">
          <h4>🔧 복구(일 단위)</h4>
          <ul class="timeline">
            <li>관공서 <b>귀가 허가</b> 전까지 해안 접근 금지</li>
            <li>침수 건물/전기·가스 <b>전문가 점검 전 사용 금지</b></li>
            <li>오염된 식수·음식 섭취 금지</li>
            <li>공식 복구·구호 안내 준수</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📝 개인 대피 체크리스트 (인쇄용)"):
        st.markdown("""
- 대피 경로와 고지대 위치 공유  
- 가족/친구 연락 방법·합류 지점 사전 합의  
- 응급키트(식수/비상식량/손전등/구급약/보온담요) 준비  
- 재난문자·라디오·관공서 방송 수신 가능 여부 점검  
- 전기·가스·수도 차단 방법 숙지
        """)
    guide_text = f"""[쓰나미 대응 요약]
- 예측 확률: {prob*100:.1f}% (기준 {threshold*100:.0f}%)
- 즉시: 해안·하천·지하차도 금지, 높은 지대 이동, 방송 확인, 추가 파도 주의
- 단기: 연락/합류, 응급키트·식수, 해안 접근 금지, 전기·가스 차단
- 복구: 귀가 허가 전 해안 금지, 침수 건물/전기·가스 점검 전 사용 금지, 오염 식수 금지
"""
    st.download_button("⬇️ 대응 요약 텍스트", guide_text, file_name="tsunami_safety_guide.txt")

# --------------------------------------------------
# (C) 데이터 입력
# --------------------------------------------------
st.sidebar.header("데이터 입력")
uploaded = st.sidebar.file_uploader("CSV 업로드(또는 리포에 포함된 파일명 입력)", type="csv")
default_path = st.sidebar.text_input("리포/로컬 CSV 경로(선택)", value="earthquake_data_tsunami.csv")

@st.cache_data
def load_df_from_source(uploaded_file, path_string):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    if path_string and os.path.exists(path_string):
        return pd.read_csv(path_string)
    # 데모(없을 때만 생성)
    rng = np.random.default_rng(42)
    n = 400
    df_demo = pd.DataFrame({
        "magnitude": rng.normal(5.5, 0.6, n).clip(3.5, 8.5),
        "depth": rng.normal(40, 25, n).clip(1, 300),
        "lat": rng.uniform(-60, 60, n),
        "lon": rng.uniform(-180, 180, n),
        "distance_to_coast": rng.exponential(200, n).clip(0, 800)
    })
    # 단순 규칙으로 라벨 생성(데모)
    logit = (df_demo["magnitude"]-5.5)*1.6 + (80-df_demo["depth"])*0.015 + (200-df_demo["distance_to_coast"])*0.005
    p = 1/(1+np.exp(-logit))
    df_demo["tsunami"] = (p > 0.55).astype(int)
    return df_demo

df = load_df_from_source(uploaded, default_path)
st.caption("데이터 미리보기")
st.dataframe(df.head(), use_container_width=True)

# --------------------------------------------------
# (D) 타깃/피처 선택
# --------------------------------------------------
cols = list(df.columns)
auto_target = next((c for c in cols if any(k in c.lower() for k in ["tsunami","label","target","occur"])), cols[-1])
target_col = st.selectbox("타깃(쓰나미 발생 여부) 컬럼 선택", options=cols, index=cols.index(auto_target))

X = df.drop(columns=[target_col])
y = df[target_col]

num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = [c for c in X.columns if c not in num_cols]
if len(num_cols) == 0:
    st.error("숫자형 피처가 필요합니다. (예: magnitude, depth, lat, lon ...)")
    st.stop()

# --------------------------------------------------
# (E) 모델 학습/저장/로드
# --------------------------------------------------
MODEL_PATH = "rf_model.pkl"
META_PATH = "rf_meta.joblib"

@st.cache_resource
def train_or_load(X, y, num_cols, cat_cols):
    # 저장된 모델 있으면 로드
    if os.path.exists(MODEL_PATH) and os.path.exists(META_PATH):
        return joblib.load(MODEL_PATH), joblib.load(META_PATH)

    # 없으면 학습
    num_pipe = Pipeline([("imp", SimpleImputer(strategy="median"))])
    cat_pipe = Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                         ("oh", OneHotEncoder(handle_unknown="ignore"))])
    pre = ColumnTransformer([("num", num_pipe, num_cols), ("cat", cat_pipe, cat_cols)])

    rf = RandomForestClassifier(
        n_estimators=300, random_state=42,
        class_weight="balanced_subsample", n_jobs=-1
    )
    pipe = Pipeline([("pre", pre), ("rf", rf)])

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    pipe.fit(Xtr, ytr)

    yhat = pipe.predict(Xte)
    ypr  = pipe.predict_proba(Xte)[:,1]
    acc = accuracy_score(yte, yhat)
    try:
        auc = roc_auc_score(yte, ypr)
    except Exception:
        auc = float("nan")

    # 슬라이더 범위(숫자형만)
    feature_ranges = {}
    for c in num_cols:
        cmin, cmax = np.nanmin(X[c].values), np.nanmax(X[c].values)
        span = max(1e-9, cmax - cmin)
        feature_ranges[c] = (float(cmin - 0.05*span), float(cmax + 0.05*span))

    meta = {
        "acc": acc, "auc": auc,
        "num_cols": num_cols, "cat_cols": cat_cols,
        "feature_ranges": feature_ranges,
        "top_numeric": num_cols[:8]  # 슬라이더 최대 8개
    }

    joblib.dump(pipe, MODEL_PATH)
    joblib.dump(meta, META_PATH)
    return pipe, meta

model, meta = train_or_load(X, y, num_cols, cat_cols)

c1, c2, c3 = st.columns(3)
with c1: st.metric("정확도(ACC)", f"{meta['acc']*100:.1f}%")
with c2: st.metric("AUC", f"{meta['auc']:.3f}" if np.isfinite(meta["auc"]) else "N/A")
with c3: st.write("학습 피처 수:", len(num_cols)+len(cat_cols))
st.divider()

# --------------------------------------------------
# (F) 탭: 예측 / 대응책 / 데이터·한계
# --------------------------------------------------
tab1, tab2, tab3 = st.tabs(["예측", "대응책", "데이터·한계"])

with tab1:
    st.subheader("🔧 슬라이더로 입력값 조절 → 쓰나미 발생 가능성 계산")

    top_feats = meta.get("top_numeric", [])
    ranges = meta.get("feature_ranges", {})

    if len(top_feats) == 0:
        st.warning("숫자형 피처가 없어 슬라이더를 만들 수 없어요.")
    else:
        # 🔴 반드시 form 내부에 제출 버튼 포함!
        with st.form("slider_form"):
            cols2 = st.columns(2)
            user_vals = {}
            for i, f in enumerate(top_feats):
                low, high = ranges.get(f, (float(np.nanmin(X[f])), float(np.nanmax(X[f]))))
                default = float(np.nanmedian(X[f]))
                with cols2[i % 2]:
                    user_vals[f] = st.slider(
                        f,
                        min_value=float(low),
                        max_value=float(high),
                        value=float(np.clip(default, low, high))
                    )

            # 범주형은 최빈값으로 자동 설정(간단화)
            cat_defaults = {}
            for c in meta["cat_cols"]:
                try:
                    cat_defaults[c] = df[c].mode().iloc[0]
                except Exception:
                    cat_defaults[c] = None

            threshold = st.slider("판정 기준(Threshold)", 0.0, 1.0, 0.5, 0.01)

            # ✅ 폼 내부에 제출 버튼 필수
            submitted = st.form_submit_button("예측하기")

        if submitted:
            base = {c: np.nan for c in X.columns}
            base.update(user_vals)
            base.update(cat_defaults)
            xin = pd.DataFrame([base])[X.columns]
            proba = float(model.predict_proba(xin)[:,1])
            pred = int(proba >= threshold)

            st.success(f"예측된 쓰나미 발생 가능성: **{proba*100:.1f}%** (기준 {threshold*100:.0f}%)")
            st.progress(min(max(proba, 0.0), 1.0))
            st.session_state["last_proba"] = proba
            st.session_state["last_threshold"] = threshold

with tab2:
    st.subheader("예측 결과 기반 대응 가이드")
    proba = st.session_state.get("last_proba", 0.23)   # 제출 전엔 예시값
    threshold = st.session_state.get("last_threshold", 0.5)
    render_safety_ui(prob=proba, threshold=threshold)

with tab3:
    st.subheader("데이터·모델 한계 및 주의")
    st.markdown("""
- **출처 예시:** USGS Earthquake Catalog, NOAA Tsunami DB  
- **한계:** 내륙/지형/해저지형/실시간 관측 미반영으로 오·미경보 가능  
- **용도:** 학습·시뮬레이션 보조. 실제 경보/정책 결정은 **공식 기관 안내 준수**
""")
    st.caption(f"작업 디렉터리: {pathlib.Path('.').resolve()}")
    st.caption(f"동일 경로 파일: {', '.join(sorted([p.name for p in pathlib.Path('.').glob('*')]))}")
