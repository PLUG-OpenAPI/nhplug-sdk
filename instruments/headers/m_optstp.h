/****************************************************************************
 * NH투자증권 종목마스터 — 국내 옵션 > 주식옵션
 *
 * @file      m_optstp.mst
 * @url       https://www.nhplug.com/instruments/m_optstp.mst
 * @record    77      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   optstp.c
 * @note      sValue는 스케일 없음(원단위)
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char sCode[9];                          /* @0    종목코드 <(K) + expcode[8]> */
    char sName[34];                         /* @9    종목명 <hname 앞 34B> */
    char sValue[17];                        /* @43   가격(행사가격) <actprice ("%17.8f")> | "%17.8f" 형식, 우측정렬(좌측 공백패딩). ※ 스케일 없음 — 지수옵션 sPrice 와 규칙이 다름 */
    char eATM[1];                           /* @60   ATM 구분 <atmgubun[1]> | 1:ATM 2:ITM 3:OTM */
    char eNew[1];                           /* @61   권리구분 <newgubun[1]> | 1:신규 2:추가 3:기존 4:최초 5:조정 6:특별 A:과거조정 B:과거특별 ※ 원장 배치가 1/2/4 를 3 으로 강제 치환 → mst 에서는 관측 불가. 신규상장 판정 불가 */
    char sStockCode[6];                     /* @62   주식 종목코드 <undershcode 앞 6B> */
    char sStockName[8];                     /* @68   주식 종목명 <undername ← hname 앞 8B> | [주의] 기초자산명 필드가 아니라 sName 앞 8바이트 복사본(실측 14,060건 전량 일치). 기초자산 조인은 sStockCode 로만 할 것 */
    char dummy[1];                          /* @76   레코드 종단자 (LF) <(LF)> */
}   OPTSTP;   /* sizeof = 77 */
