import streamlit as st

def render_tsunami_safety_ui(prob: float, threshold: float = 0.5):
    # ---------- 미니 CSS(카드/배지/타임라인) ----------
    st.markdown("""
    <style>
      .banner { 
        padding: 14px 16px; border-radius: 14px; 
        background: linear-gradient(135deg,#1f6feb, #7c3aed);
        color: white; box-shadow: 0 10px 18px rgba(0,0,0,.10); 
        margin-bottom: 12px;
      }
      .chip {
        display:inline-block; padding:6px 10px; border-radius:16px; 
        background: rgba(255,255,255,.20); color: #fff; font-weight:600; 
        margin-right:8px; font-size:.85rem;
      }
      .card {
        border-radius:16px; padding:16px; background:#ffffff; 
        border:1px solid #ececec; box-shadow:0 8px 16px rgba(0,0,0,.06);
        height:100%;
      }
      .card h4 { margin:0 0 8px 0; }
      .ok { background: #ecfdf5; border-color:#d1fae5; }
      .warn { background: #fff7ed; border-color:#ffedd5; }
      .danger { background: #fef2f2; border-color:#fee2e2; }
      .badge {
        display:inline-block; padding:4px 8px; border-radius:10px; 
        font-size:.8rem; font-weight:700; color:#fff;
      }
      .badge-red{ background:#ef4444; }
      .badge-amber{ background:#f59e0b; }
      .badge-green{ background:#10b981; }
      .timeline { list-style:none; padding-left:0; }
      .timeline li {
        margin:10px 0; padding-left:12px; border-left:3px solid #e5e7eb;
      }
    </style>
    """, unsafe_allow_html=True)

    # ---------- 배너 / 확률 상태 ----------
    st.markdown(f"""
    <div class="banner">
      <div style="display:flex; align-items:center; gap:12px;">
        <div style="font-size:1.2rem;">🌊 <b>쓰나미 대응 가이드</b></div>
      </div>
      <div style="margin-top:8px;">
        <span class="chip">예측 확률: {prob*100:.1f}%</span>
        <span class="chip">판정 기준: {threshold*100:.0f}%</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 상태 배지
    if prob >= threshold:
        st.markdown('<span class="badge badge-red">위험도: 높음</span>', unsafe_allow_html=True)
        tone = "danger"
        lead = "🚨 예측: 발생 가능성 ‘높음’ — 즉시 대피 절차를 확인하세요."
    elif prob >= threshold*0.6:
        st.markdown('<span class="badge badge-amber">위험도: 중간</span>', unsafe_allow_html=True)
        tone = "warn"
        lead = "⚠️ 예측: 주의 — 경보·방송을 확인하고 대피 경로를 점검하세요."
    else:
        st.markdown('<span class="badge badge-green">위험도: 낮음</span>', unsafe_allow_html=True)
        tone = "ok"
        lead = "✅ 예측: 낮음 — 그래도 해안 지역에서는 항상 대피 경로를 숙지하세요."

    st.write("")
    st.info(lead)

    # ---------- 3단 레이아웃(즉시/단기/복구) ----------
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

    st.write("")
    # 체크리스트(발표용 깔끔)
    with st.expander("📝 개인 대피 체크리스트 (프린트/복사용)"):
        st.markdown("""
- 대피 경로와 고지대 위치를 팀원과 공유했는가  
- 가족/친구와 연락 방법·합류 지점을 정했는가  
- 응급키트(식수, 비상식량, 손전등, 구급약, 보온용 담요)를 준비했는가  
- 재난문자/라디오/관공서 방송을 수신 가능한가  
- 전기·가스·수도 차단 방법을 알고 있는가
        """)

    # 다운로드 버튼(학습지/포스터용 텍스트)
    guide_text = f"""[쓰나미 대응 요약]
- 예측 확률: {prob*100:.1f}%, 기준 {threshold*100:.0f}%
- 즉시: 해안·하천·지하차도 접근 금지, 높은 지대로 이동, 방송 확인, 추가 파도 주의
- 단기: 연락/합류, 응급키트·식수, 해안 접근 금지, 전기·가스 차단
- 복구: 귀가 허가 전 해안 금지, 침수 건물/전기·가스 점검 전 사용 금지, 오염 식수 금지
"""
    st.download_button("⬇️ 대응 요약 텍스트 저장", guide_text, file_name="tsunami_safety_guide.txt")

# 예: 예측 확률 변수 proba를 사용한다면
# render_tsunami_safety_ui(prob=proba, threshold=0.5)
