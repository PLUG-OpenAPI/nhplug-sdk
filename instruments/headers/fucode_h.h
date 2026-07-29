/****************************************************************************
 * NH투자증권 종목마스터 — 해외파생 > 선물 > CME지수선물
 *
 * @file      fucode_h.mst
 * @url       https://www.nhplug.com/instruments/fucode_h.mst
 * @record    283      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   d6890
 * @note      실제 구성은 에너지 70% / 지수 18% / 금속 12%
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char Symbol[32];                        /* @0    종목코드 (시세 제공사 코드) <symb> */
    char InnerSymbol[32];                   /* @32   내부종목코드 (당사 원장-시세 코드) <isym> */
    char CoreSymbol[12];                    /* @64   원장종목코드 (원장 생성 단축코드) <csym> */
    char inrt[32];                          /* @76   내부품목코드 */
    char ExchName[8];                       /* @108  거래소명 (예 FCME = CME 선물) <exnm> | fucode_h = "FCME" 전량 / fucode_fhke_h = "FHKE" 전량 */
    char EngName[80];                       /* @116  종목영문명 <enam> */
    char ExchId[3];                         /* @196  거래소IDX <exid> | E01:CME Group E02:SGX E03:HKEx E04:Eurex E06:CBOE E07:ASX E08:BM&F E09:TAIFEX E10:LME E11:ICE US E12:OSE E13:ICE Europe E14:Euronext E16:OPRA E18:NSE */
    char SymbolType[1];                     /* @199  종목유형 <styp> | F:선물 (실측 전량 F) */
    char Section[2];                        /* @200  상품그룹코드 <sect> | 10:통화 20:이자 30:지수 40:상품 50:금속 60:에너지 80:단일주식 90:기타상품 */
    char Pind[1];                           /* @202  가격표시자 (진법 표시) <pind> | 0:1/1 1:1/10 2:1/100 3:1/1000 4:1/10^4 5:1/10^5 6:1/10^6 7:1/10^7 8:1/10^8 A:1/2 B:1/4 C:1/8 D:1/16 E:1/32 F:1/64 G:1/128 H:1/256 I:0.5/32 J:0.5/64 K:0.25/32 L:0.125/32 */
    char Tradable[1];                       /* @203  거래가능유무 <trdf> | 0:거래가능 1:거래불가 */
    char Onoff[1];                          /* @204  온오프라인구분 <onof> | 0:전체 1:직원 */
    char TickSize[17];                      /* @205  최소가격변동폭 <pinc> */
    char AdjustValue[17];                   /* @222  가격조정계수 <adjv> */
    char Leadmonth[1];                      /* @239  선도월물 <ledm> | 1:선도월물(거래량 최다) 0:그외 */
    char MonthYear[8];                      /* @240  만기년월 (YYYYMM) <exym> | 실측은 YYYYMMDD 8자리 최종거래일. ※ 영문명 말미의 -YYMM 은 인도월이며 에너지·일부 금속은 최종거래일과 월이 다름 */
    char PrevLast[17];                      /* @248  전일 종가(정산가) <base> */
    char TickValue[17];                     /* @265  틱가치 (한 틱당 가치) <tval> */
    char dummy[1];                          /* @282  레코드 종단자 (LF) <(LF)> */
}   FUCODE_H;   /* sizeof = 283 */
