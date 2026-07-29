/****************************************************************************
 * NH투자증권 종목마스터 — 국내 선물 > 섹터지수선물 스프레드
 *
 * @file      m_new_xfutsp.mst
 * @url       https://www.nhplug.com/instruments/m_new_xfutsp.mst
 * @record    139      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   xfutsp.c(.nouse)
 * @note      원장 엑셀 시트가 구버전(95B). 현행 139B
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char sCode[9];                          /* @0    종목코드 <(K) + expcode[8]> */
    char sName[80];                         /* @9    종목명 <hname[80]> */
    char sBaseCode[3];                      /* @89   기초자산코드 <underid[3]> */
    char sUnderupcode[6];                   /* @92   업종코드 <under_upcode[6]> */
    char sBaseName[40];                     /* @98   기초자산명 <underhname[40]> */
    char dummy2[1];                         /* @138  레코드 종단자 (LF) <(LF)> */
}   NEW_XFUTSP;   /* sizeof = 139 */
