/****************************************************************************
 * NH투자증권 종목마스터 — 국내주식
 *
 * @file      m_new_stock.mst
 * @url       https://www.nhplug.com/instruments/m_new_stock.mst
 * @record    237      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   IVDSTKMST01
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char sCode[6];                          /* @0    종목코드 <shrn_iscd> */
    char sMarket[1];                        /* @6    시장 분류 구분 코드 <mrkt_div_cls_code> | 1:코스피 4:코스닥 A:ETN(코스피) */
    char sKorName[41];                      /* @7    한글 종목명 <hts_kor_isnm> | 선두 1바이트 마커 — * : KOSPI200 구성종목(200건), # : 코스닥150 구성종목(150건). 정렬·검색 키로 쓸 때 반드시 제거 */
    char sEngName[41];                      /* @48   영문 종목명 <hts_eng_isnm> */
    char sOldName[40];                      /* @89   구 종목명 <hts_bef_kor_isnm> */
    char eCapSize[1];                       /* @129  자본금 규모 <avls_scal_cls_code> | [시장별 상이] 코스피 1:대형주 2:중형주 3:소형주 / 코스닥 1:KOSDAQ100 2:KOSDAQ MID300 3:KOSDAQ SMALL / 0:미산정(우선주 등, 정의없음) / 공백:ETF·ETN */
    char sUpCodeM[6];                       /* @130  업종코드 중분류 <bstp_medm_div_code> | 접두 K=코스피 / Q=코스닥. 000000 = 미분류(ETF·ETN) */
    char sUpCodeS[6];                       /* @136  업종코드 소분류 <bstp_smal_div_code> | 실측 000000(727건) 외 전량 공백 — 현재 미사용 */
    char sGroup[2];                         /* @142  그룹 코드 <h_grp_code> */
    char gManuf[1];                         /* @144  제조업 구분 <mnin_cls_code_yn> <manuf> | Y:제조업 N:그외 (실측 전량 N — 사실상 미사용) */
    char sParvalue[7];                      /* @145  액면가 <stck_fcam> */
    char sPrePrice[7];                      /* @152  전일종가 <stck_prdy_clpr> (신규는 평가가격) */
    char eRights[1];                        /* @159  신규/권리락 <nh_rights> | 0:정상 1:권리락 2:배당락 6:신규종목 / 실측 i(179건)·j(1건) 는 정의 없음 (소스가 이 필드를 읽지 않음) */
    char eUnder[1];                         /* @160  관리종목 <mang_issu_yn> | N:정상 Y:관리종목 */
    char eStop[1];                          /* @161  거래정지 <trht_yn> | N:정상 Y:거래정지 */
    char eWarn[1];                          /* @162  투자유의 <warn_yn> | N:정상 Y:지정 */
    char eGongsi[1];                        /* @163  불성실공시 <insn_pbnt_yn> | N:정상 Y:불성실공시 */
    char gTonghap[1];                       /* @164  통합지수 <krx100_issu_yn> | Y:KRX100 편입 N:미편입 공백:판정대상 아님(ETF·ETN 등 828건) */
    char gVenture[1];                       /* @165  종목구분추가 <bu12> | [시장별 상이] 코스피 0:일반 4:외국기업(추정) 5:투자회사 6:리츠 8:ETF 9:선박투자회사 A:인프라투융자회사 F:X클래스(추정) / 코스닥 A:우량기업 B:벤처기업 C:중견기업 D:신성장기업 / ETN E */
    char gKrx300[1];                        /* @166  KRX300 구분 <krx300_yn> | Y:KRX300 편입 N:미편입 공백:판정대상 아님 */
    char gKospi50[1];                       /* @167  코스피50 구분 <kospi50_issu_yn> | Y:KOSPI50 편입(50건) N:미편입 공백:판정대상 아님 */
    char eAccept[1];                        /* @168  채용구분[KOSPI200] <kospi200_apnt_cls_code> | KOSPI200 산업군 11종 — 0:미편입 1:건설기계 2:중공업 3:철강소재 4:에너지화학 5:정보통신 6:금융 7:생활소비재 8:경기소비재 9:산업재 A:건강관리 B:CS/반도체 ※ 0 이 아니면 KOSPI200 구성종목(200건) */
    char gKospiIT[1];                       /* @169  코스피 지배구조 구분 <sprn_strr_sprr_yn> | 실측 N 4,295 / Y 2 — 사실상 미사용 */
    char gKospiBD[1];                       /* @170  코스피 배당 구분 <kospidiv> | 실측 전량 공백 — 현재 미사용 */
    char gIT[1];                            /* @171  코스닥 IT 구분 <itgubun> | 1:코스닥 IT 해당(228건) 공백:그외 */
    char gKosdaq150[1];                     /* @172  코스닥150 구분 <kosdaq150_yn> | Y:코스닥150 편입(150건) N:미편입 공백:판정대상 아님 */
    char gKospi100[1];                      /* @173  코스피100 구분 <kospi100_issu_yn> | Y:KOSPI100 편입(100건) N:미편입 공백:판정대상 아님 */
    char prdy_avls[12];                     /* @174  전일 시가총액(억) */
    char invt_epmd_issu_yn[1];              /* @186  투자유의종목여부 */
    char short_over_issu_cls_code[1];       /* @187  단기과열구분코드 | 0:해당없음 1:단기과열예고 2:단기과열지정 3:단기과열연장 */
    char alert_gb[1];                       /* @188  투자주의경고구분코드 | 0:해당없음 1:투자주의 2:투자경고 3:투자주의·투자위험예고 4:투자경고·투자위험예고 5:투자위험 */
    char sltr_yn[1];                        /* @189  정리매매여부 | Y:정리매매종목 N:해당없음 */
    char stck_sdpr[7];                      /* @190  기준가 */
    char nxt_yn[1];                         /* @197  NXT 거래소 종목 여부 <nxt_yn> | Y:NXT 거래대상 N:해당없음 */
    char eNXTStop[1];                       /* @198  NXT 거래정지 <nxt_trht_yn> | N:정상 Y:NXT 거래정지 */
    char sUpCodeL[6];                       /* @199  업종코드 대분류 <bstp_larg_div_code> | 접두 K=코스피 / Q=코스닥. 000000 = 미분류(ETF·ETN) */
    char nxt_comp_deal_tr_code[2];          /* @205  NXT경쟁매매거래허용코드 (bitwise) | 비트합의 10진 문자열 — 1:프리마켓 2:메인마켓 4:애프터마켓 8:종가보드 (실측 전량 "15" = 전체허용) */
    char filler[29];                        /* @207  filler */
    char dummy[1];                          /* @236  레코드 종단자 (LF) <(LF)> */
}   NEW_STOCK;   /* sizeof = 237 */
