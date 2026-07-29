/****************************************************************************
 * NH투자증권 종목마스터 — 국내 옵션 > 코스닥150위클리옵션
 *
 * @file      m_qoption.mst
 * @url       https://www.nhplug.com/instruments/m_qoption.mst
 * @record    25      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   IVANOPMST01
 * @note      전문 28B → mst 25B (주야간/상품코드 제거)
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char sCode[9];                          /* @0    종목코드 <SHRN_ISCD> */
    char sCallPut[2];                       /* @9    콜/풋 구분 <CP_TYPE> | CP949 한글 2바이트 — "콜"(C4 DD) / "풋"(C7 B2). ASCII C/P 아님 */
    char sMonth[6];                         /* @11   년월(월물) <MTRT_YYMM> | YYMMWW (년·월·주차). ※ 일자 아님 */
    char sPrice[6];                         /* @17   행사가격 <ACPR> | ※ 실제 행사가 × 100 (0 좌측패딩). 예 82500 → 825.00. 반드시 /100 할 것 */
    char eATM[1];                           /* @23   ATM 구분 <ATM_CLS_CODE> | 1:ATM 2:ITM 3:OTM */
    char dummy[1];                          /* @24   레코드 종단자 (LF) <(LF)> */
}   QOPTION;   /* sizeof = 25 */
