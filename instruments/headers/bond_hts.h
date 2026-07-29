/****************************************************************************
 * NH투자증권 종목마스터 — 국내 장내채권
 *
 * @file      bond_hts.mst
 * @url       https://www.nhplug.com/instruments/bond_hts.mst
 * @record    251      // 레코드 크기(byte). 파일크기 % record == 0 이어야 함
 * @encoding  CP949
 * @padding   공백(0x20) 우측 · 레코드 끝 1바이트 LF(0x0A) · 파일 헤더 없음
 * @service   IVOBONREQ04
 * @note      전문 대비 bond_type/filler 추가, 시세 6필드 제외
 *
 * 파싱 주의: 반드시 'rb'(바이너리) 로 열 것. NUL 종료 문자열이 아니므로
 *           strlen 금지 — 길이 기반 슬라이싱 후 우측 공백 제거.
 ***************************************************************************/

#pragma pack(1)
typedef struct
{
    char bond_type[1];                      /* @0    채권타입 <(mst 전용)> | A,3,4:일반형 1,5,9:주식형 2:소액채권 (공백 33건 = 분류 미수신) */
    char bond_shrn_iscd[9];                 /* @1    채권단축종목코드 <BOND_SHRN_ISCD> */
    char bond_stnd_iscd[12];                /* @10   채권표준종목코드 <BOND_STND_ISCD> */
    char bond_isnm[80];                     /* @22   채권종목명 <BOND_ISNM> */
    char srfc_mnrt[6];                      /* @102  표면금리 (소수점 3자리, 예 "5.990") <SRFC_MNRT> | 원장 타입 double 6.3 → 전체폭 6·소수 3자리, 우측정렬(좌측 공백패딩). 예 " 2.500" */
    char pblc_date[8];                      /* @108  발행일 (YYYYMMDD) <PBLC_DATE> */
    char rdmp_date[8];                      /* @116  만기일 (YYYYMMDD) <RDMP_DATE> | YYYYMMDD. 99991231 = 만기 없음(영구채) */
    char cfd_grd_cd[4];                     /* @124  신용등급 (예 BBB / AAA / AA-) <CFD_GRD_CD> | 신용등급 좌측정렬(AAA/AA-/BBB+ 등). "_" = 무등급·등급미부여(4,431건, 국채·지방채 전량) */
    char bnd_tp_cd[2];                      /* @128  채권종류코드 <BND_TP_CD> | AB:특수채 CO:회사채 FO:외국채 GB:국채 MB:지방채 */
    char bnd_tp_cd_nm[20];                  /* @130  채권종류코드명 <BND_TP_CD_NM> | bnd_tp_cd 와 1:1 고정 대응. 판정은 코드로, 명칭은 표시용 */
    char filler[100];                       /* @150  필러 <(mst 전용)> */
    char dummy[1];                          /* @250  레코드 종단자 (LF) <(LF)> */
}   BOND_HTS;   /* sizeof = 251 */
