import streamlit as st
st.title('김민지 저리가')
a=st.text_input('김민지의 장점을 써주세요!')
b=st.selectbox('김민지의 단점을 선택하세요!',['말이 많다','목소리가 크다','시끄럽다'])
if st.button('김민지 바보'): 
  st.write('당신도 민지가 바보라고 생각하시는군요!')
  st.info(a+'정답입니다!')
  st.warning(b+'   역시나')
  st.balloons()
