/****************************************************************************
 * NH투자증권 종목마스터 — 해외파생 > 옵션 > OPRA주식옵션
 *
 * @file      opcode_h.mst
 * @url       https://www.nhplug.com/instruments/opcode_h.mst
 * @record    259      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   d6891
 * @note      헤더 주석 258B 는 오류. 실제 259B
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
    char ExchName[8];                       /* @108  거래소명 (예 OOPR = OPRA 미국 개별주식옵션) <exnm> | opcode_h = "OOPR" 전량 / opcode_ohke_h = "OHKE" 전량 */
    char EngName[80];                       /* @116  종목영문명 <enam> */
    char UnderCode[15];                     /* @196  기초자산코드 (Underlying Code) <unps1> */
    char StrikePrice[17];                   /* @211  행사가 <strk> */
    char OptionType[1];                     /* @228  옵션유형 (콜/풋 구분) <corp> | C:Call P:Put */
    char AtmFlag[1];                        /* @229  행사가능유무 <atmf> | 1:ATM(등가격) 0:그외 */
    char MonthYear[8];                      /* @230  만기년월 (YYYYMM 또는 YYYYMMDD) <exym> | YYYYMMDD 만기년월일 */
    char PrevLast[17];                      /* @238  전일 종가(정산가) <base> */
    char Pind[1];                           /* @255  가격표시자 (진법 표시) <pind> | 0:1/1 1:1/10 2:1/100 3:1/1000 4:1/10^4 5:1/10^5 6:1/10^6 7:1/10^7 8:1/10^8 A:1/2 B:1/4 C:1/8 D:1/16 E:1/32 F:1/64 G:1/128 H:1/256 I:0.5/32 J:0.5/64 K:0.25/32 L:0.125/32 */
    char WeekMonthly[1];                    /* @256  주월구분 <wmgb> | W:Weekly M:Monthly */
    char Onoff[1];                          /* @257  온/오프 구분 <onof> | 0:전체 1:직원 */
    char dummy[1];                          /* @258  레코드 종단자 (LF) <(LF)> */
}   OPCODE_H;   /* sizeof = 259 */
