/****************************************************************************
 * NH투자증권 종목마스터 — 해외파생 > 상품정보
 *
 * @file      foitem_h.mst
 * @url       https://www.nhplug.com/instruments/foitem_h.mst
 * @record    310      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   d6892
 * @note      종목이 아닌 품목 마스터. 배포 URL 확인 필요
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char ExchCd[8];                         /* @0    거래소명 (예 OPRA) <exnm> */
    char inrt[32];                          /* @8    내부품목코드 | ExchCd + inrt 조합이 이 파일의 PK. fucode_* /opcode_* 와 조인 키 */
    char ExchId[3];                         /* @40   거래소IDX <exid> | E01:CME Group E02:SGX E03:HKEx E04:Eurex E06:CBOE E07:ASX E08:BM&F E09:TAIFEX E10:LME E11:ICE US E12:OSE E13:ICE Europe E14:Euronext E16:OPRA E18:NSE */
    char EngName[80];                       /* @43   품목영문명 <enam> */
    char UnderCode[15];                     /* @123  기초자산코드 (국가코드3 + unps 끝2자리 제거) <unps1> */
    char SymbolType[1];                     /* @138  종목유형 <styp> | F:선물 O:옵션 */
    char Tradable[1];                       /* @139  거래가능유무 <trdf> | 0:거래가능 1:거래불가 */
    char Section[2];                        /* @140  상품그룹코드 <sect> | 10:통화 20:이자 30:지수 40:상품 50:금속 60:에너지 80:단일주식 90:기타상품 */
    char Pind[1];                           /* @142  가격표시자 (진법 표시) <pind> | 0:1/1 1:1/10 2:1/100 3:1/1000 4:1/10^4 5:1/10^5 6:1/10^6 7:1/10^7 8:1/10^8 A:1/2 B:1/4 C:1/8 D:1/16 E:1/32 F:1/64 G:1/128 H:1/256 I:0.5/32 J:0.5/64 K:0.25/32 L:0.125/32 */
    char TickSize[17];                      /* @143  최소가격변동폭 <pinc> */
    char TickValue[17];                     /* @160  틱가치 <tval> */
    char AdjustValue[17];                   /* @177  가격조정계수 <adjv> | 실측 전량 1.000000000 — 현재 단일값 */
    char StrikePind[10];                    /* @194  행사가 소숫점자리수 <stpd> */
    char OptionStyle[1];                    /* @204  옵션행사유형 <opts> | [적재 오류] 정의는 1:American 2:European 이나 실측은 F/O (SymbolType 과 동일). 이 필드로 행사유형 판정 금지 */
    char Onoff[1];                          /* @205  온오프라인구분 <onof> | 0:전체 1:직원 */
    char opbr[17];                          /* @206  옵션프리미엄 기준가격 (옵션만) */
    char oppb[17];                          /* @223  옵션프리미엄 이하 틱사이즈 (옵션만) */
    char oppo[17];                          /* @240  옵션프리미엄 이상 틱사이즈 (옵션만) */
    char opbv[17];                          /* @257  옵션프리미엄 이하 틱가치 (옵션만) */
    char opov[17];                          /* @274  옵션프리미엄 이상 틱가치 (옵션만) */
    char fsmc[1];                           /* @291  결제방식 | 1:현금 2:실물 */
    char feamt[17];                         /* @292  해외파생증거금액 */
    char dummy[1];                          /* @309  레코드 종단자 (LF) <(LF)> */
}   FOITEM_H;   /* sizeof = 310 */
