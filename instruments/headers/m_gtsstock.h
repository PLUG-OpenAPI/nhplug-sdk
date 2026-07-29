/****************************************************************************
 * NH투자증권 종목마스터 — 해외주식
 *
 * @file      m_gtsstock.mst
 * @url       https://www.nhplug.com/instruments/m_gtsstock.mst
 * @record    164      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   g6925
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char sGIC[15];                          /* @0    GIC (해외종목 내부 통합코드) <gic> */
    char sKorName[40];                      /* @15   한글종목명 <kor_name> */
    char sEngName[40];                      /* @55   영문종목명 <eng_name> */
    char sNationCode[3];                    /* @95   국가코드 <country_code> */
    char sSymbol[12];                       /* @98   심벌 <symbol> */
    char sStockCode[3];                     /* @110  거래소코드 <exch_id> */
    char sStandardCode[12];                 /* @113  표준코드 <isin_code> */
    char gIssue[2];                         /* @125  종목구분 <com_kind> | 코드표 없음. 실측 추정 — 01:보통주 02:하이브리드 03:Unit Trust 06:Stapled Unit 07:CDI 09:신주인수권 10:펀드 12:ETF 13:ETB 14:실물상품ETC */
    char gIndustryReuter[4];                /* @127  로이터업종코드 <industry_group> */
    char sIndustryKorea[4];                 /* @131  한국업종코드 <kor_ind_code> | 실측 9999 / 공백 뿐 — 사실상 미사용 */
    char gLock[2];                          /* @135  락구분 <lock_cls> | 코드값 정의 없음 (헤더·원장·소스 어디에도 없음). 실측 "1 " 5,778 / 공백 3,391 */
    char gPosTrade[1];                      /* @137  거래가능구분 <trade_flag> | 실측 전량 1 — 현재 단일값 */
    char gPayMoney[3];                      /* @138  결제화폐 <currency_unit> */
    char gListed[1];                        /* @141  상장구분 <list_cls> | 실측 전량 0 — 현재 단일값 */
    char gTOPIX100[1];                      /* @142  일본 TOPIX100 구분 <topx_cls> | [명칭과 실제 용도 상이] 1 = 일본 TOPIX100 편입 + 비(非)일본은 ETF 여부(gIssue=12)로 재사용 */
    char sOriginNationCode[3];              /* @143  원종목국가코드 <p_country_code> */
    char sOriginSymbol[12];                 /* @146  원종목심벌 <p_symbol> */
    char sOriginCurrency[3];                /* @158  원종목통화 <p_currency_id> */
    char sDecimalPoint[1];                  /* @161  소수점자리수 <decimal> | 가격 소수점 자릿수. CHN 2 / AUS·IDN·VNM·GBR·HKG·DEU 3 / USA 4 / JPN 0~1 */
    char sTradePoint[1];                    /* @162  소수점매매 <decimal_yn> | Y:소수점 단위 매매 가능(전량 USA 509건) N:불가 */
    char dummy[1];                          /* @163  레코드 종단자 (LF) <(LF)> */
}   GTSSTOCK;   /* sizeof = 164 */
