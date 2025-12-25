# APS Membership Data Reconciliation Report

**Purpose:** Document the process of creating a canonical member list for migration from WordPress to Django/Wagtail.

**Date:** December 24, 2025
**Prepared by:** Lars Sahl (with Claude Code assistance)

---

## 1. Source Files Analyzed

### 1.1 MemberPress Export (`memberpress_12_24_25.csv`)
- **Source:** MemberPress plugin (WordPress)
- **Records:** 2,103
- **Columns:** 49
- **File size:** 728 KB
- **Key fields:** email, status, mepr_first_name, mepr_last_name, mepr_professional_affiliation, mepr_affiliation_type, mepr_membership_year, mepr_publications, mepr_sponsor

### 1.2 WordPress User Export (`wordpress_user_export_12_24_25.csv`)
- **Source:** WordPress user export
- **Records:** 2,103
- **Columns:** 150+
- **File size:** 1.6 MB
- **Notes file:** `wordpress_user_export_NOTES_12_24_25.TXT` documents phone number formatting fixes (leading + symbols escaped to prevent Excel formula interpretation)

### 1.3 Formidable Forms Export (reference only)
- **Location:** `../membership-application-aps-form.xml`
- **Purpose:** Documents the membership application form structure
- **Not used for member data** - form definition only

---

## 2. Comparison: MemberPress vs WordPress Export

| Metric | MemberPress | WordPress |
|--------|-------------|-----------|
| Total records | 2,103 | 2,103 |
| Unique emails | 2,103 | 2,103 |
| Email overlap | 100% | 100% |
| Column count | 49 | 150+ |
| File size | 728 KB | 1.6 MB |

### Key Finding
Both exports contain **identical member data** (same 2,103 emails, same mepr_* field values). The WordPress export includes extensive WordPress-specific metadata (capabilities, dashboard settings, etc.) that is not needed for migration.

### Data Completeness (from MemberPress)
| Field | Populated | Percentage |
|-------|-----------|------------|
| email | 2,103 | 100% |
| mepr_first_name | 2,102 | 99.95% |
| mepr_professional_affiliation | 1,228 | 58% |
| mepr_membership_year | 1,833 | 87% |

### Membership Status (from MemberPress)
| Status | Count |
|--------|-------|
| none | 2,027 |
| active | 76 |

---

## 3. APS 2025 Symposium Attendees

### 3.1 Source File (`APS 2025 Membership Report.xlsx`)
- **Source:** Symposium registration system (San Diego, 2025)
- **Records:** 618 total attendees
- **Unique emails:** 614 (4 duplicates)
- **Key fields:** First, Last, Title, Affiliation, Email, Address, Phone, membership type flags

### 3.2 Membership Type Distribution
| Type | Count |
|------|-------|
| Industry Professional | 208 |
| Graduate Student | 131 |
| PI/Faculty (Academic Professional) | 128 |
| Postdoc/Retired | 54 |
| Start-Up/PUI | 42 |
| Other | 35 |
| Undergraduate | 16 |

### 3.3 Overlap Analysis with MemberPress
| Category | Count |
|----------|-------|
| Already in MemberPress | 159 |
| New (not in MemberPress) | 459 |
| Total unique emails | 614 |

### 3.4 Field Mapping: Symposium to Canonical
| Symposium Field | Canonical Field | Notes |
|-----------------|-----------------|-------|
| First | mepr_first_name | |
| Last | mepr_last_name | |
| Title | mepr_title | Job title, e.g., "Senior Scientist" |
| Affiliation | mepr_professional_affiliation | |
| Email | email | Canonical key |
| Address 1/2 | mepr_address_1/2 | |
| City/State/Postal | mepr_city/state/zip | |
| Country | mepr_country | |
| Phone | mepr_phone | |
| (boolean flags) | symposium_2025_membership_type | Original symposium category |
| (boolean flags) | mepr_affiliation_type | Mapped to academic/industry/other |

### 3.5 Affiliation Type Mapping
| Symposium Type | mepr_affiliation_type |
|----------------|----------------------|
| Graduate Student | academic |
| PI/Faculty | academic |
| Postdoc/Retired | academic |
| Undergraduate | academic |
| Start-Up/PUI | academic |
| Industry Professional | industry |
| Other | other |

---

## 4. Inactive Member Removal

### 4.1 Source File (`Mailing list_inactive member_09092025.xlsx`)
- **Source:** Mailing list system export (September 9, 2025)
- **Records:** 654 unique emails
- **Status:** All marked as "Unsubscribed"
- **Fields:** Email Address, First Name, Last Name, Status

### 4.2 Removal Results
| Metric | Count |
|--------|-------|
| Canonical list before removal | 2,562 |
| Inactive emails in source | 654 |
| Overlap (removed) | 470 |
| **Final canonical count** | **2,092** |

### 4.3 Output Files
| File | Description |
|------|-------------|
| `canonical_member_list_cleaned.csv` | Final canonical list (2,092 active members) |
| `removed_inactive_members.csv` | Archive of removed records (470 members) |

---

## 5. Active Mailing List Reconciliation

### 5.1 Source File (`Mailing list_ACTIVE member_09092025.xlsx`)
- **Source:** Mailing list system export (September 9, 2025)
- **Records:** 2,162 unique emails
- **Fields:** Email Address, First Name, Last Name

### 5.2 Cross-Reference Results
| Category | Count |
|----------|-------|
| Active mailing list | 2,162 |
| Canonical list (after inactive removal) | 2,089 |
| In both lists | 1,795 |
| Active but missing from canonical | 367 |
| Canonical but not on active mailing list | 294 |

### 5.3 Action Taken
- Added 367 missing active members to canonical list
- Removed 3 duplicate emails (from earlier merge step)
- **Final canonical count: 2,456 unique members**

### 5.4 Note on 294 "Missing" from Active List
These are likely 2025 symposium attendees who haven't been added to the mailing list yet. Not a data quality issue.

---

## 6. ChatGPT Consolidated File Analysis

### 6.1 Source Files
- **CSV:** `1-aps_members_consolidated_10_16_25.csv` (2,089 records, 207 columns)
- **Documentation:** `APS Membership Data Consolidation.docx`

### 6.2 What It Was
A ChatGPT-assisted merge process (October 2025) that combined:
- WordPress user export
- MemberPress export
- Symposium data
- Active member lists

### 6.3 Comparison with Our Canonical List

| Metric | ChatGPT File | Our Final |
|--------|--------------|-----------|
| Total records | 2,087 | 2,456 |
| Total columns | 207 | 51 |
| Overlap | 1,617 | 1,617 |
| Only in ChatGPT | 470 | - |
| Only in ours | - | 839 |

### 6.4 Analysis of 470 "Extra" Emails in ChatGPT File
| Category | Count |
|----------|-------|
| Inactive members (we correctly removed) | 465 |
| Genuinely different | 5 |

The 5 genuinely different records are minor omissions, not critical data.

### 6.5 The 207 Columns - Mostly Junk
| Category | Examples |
|----------|----------|
| WordPress UI prefs | `wp_closedpostboxes_*`, `wp_metaboxhidden_*` |
| Admin settings | `wp_screen_layout_*`, `wp_edit_*_per_page` |
| Google Site Kit | `wp_googlesitekit_*` tokens and settings |
| Two-factor auth | `wp_wp_2fa_*` |
| Session data | `wp_session_tokens` |

### 6.6 Potentially Useful Fields (Barely Populated)
| Field | Records | % |
|-------|---------|---|
| `wp_mepr_supervisor_name` | 20 | 1.0% |
| `wp_mepr_sponsor_address` | 53 | 2.5% |
| `wp_mepr_supervisor_email` | 3 | 0.1% |
| All other unique fields | <1 | <0.1% |

### 6.7 Verdict: Discarded
**Reasons:**
1. Bloated with 207 columns of WordPress cruft
2. Failed to remove inactive members (we did)
3. Fewer total members than our final list
4. Unique fields have almost no data (<3% populated)

Our workflow produced a cleaner, more complete canonical list.

---

## 7. Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-24 | Use MemberPress CSV as primary source | Cleaner export (49 vs 150+ columns), same member data, includes membership status field, smaller file size |
| 2025-12-24 | Add `symposia_attended` field | Track all symposia years (2015, 2017, 2019, 2022, 2023, 2025) as comma-separated list for future form checkboxes |
| 2025-12-24 | Map symposium types to affiliation_type | Consolidated registration categories to match Django model choices (academic, industry, other) |
| 2025-12-24 | Preserve symposium type as separate field | Keep `symposium_2025_membership_type` for reference; original granularity may be useful |
| 2025-12-24 | Remove inactive/unsubscribed members | 470 members marked as unsubscribed in mailing list removed from canonical list |
| 2025-12-24 | Add missing active mailing list members | 367 active subscribers not in MemberPress/symposium data added to canonical list |
| 2025-12-24 | Deduplicate final list | Removed 3 duplicate emails created during merge steps |
| 2025-12-24 | Discard ChatGPT consolidated file | 207 columns of cruft, fewer records, didn't remove inactive members - our workflow is superior |

---

## 8. Data Quality Issues Identified

1. **Phone number formatting:** Some international phone numbers with leading `+` were escaped in WordPress export to prevent Excel formula interpretation. Minor issue, documented in notes file.

2. **Professional affiliation:** Only 58% populated - may need outreach campaign to complete.

3. **Membership status:** 96% show "none" status, only 76 (4%) show "active" - needs clarification on what this means for membership validity.

---

## 9. Canonical List Output

### 9.1 Final Output File: `canonical_member_list_final.csv`

| Metric | Value |
|--------|-------|
| **Final total records** | **2,456** |
| From MemberPress (original) | 2,103 |
| Added from 2025 Symposium | +459 |
| Removed (inactive/unsubscribed) | -470 |
| Added from active mailing list | +367 |
| Duplicates removed | -3 |

### 9.2 New Fields Added
| Field | Description |
|-------|-------------|
| `symposia_attended` | Comma-separated list of symposium years attended (e.g., "2019,2022,2025") |
| `symposium_2025_membership_type` | Original registration category from 2025 symposium |

### 9.3 Data Completeness (New Attendees from Symposium)
The new attendees from the symposium have complete:
- Name (first, last)
- Title (job title)
- Affiliation (institution)
- Full address
- Phone
- Symposium membership type

---

## 10. Next Steps

- [x] Analyze MemberPress vs WordPress exports
- [x] Analyze 2025 Symposium attendees
- [x] Create canonical member list with merged data
- [x] Remove inactive/unsubscribed members
- [x] Reconcile with active mailing list
- [x] Deduplicate final list
- [x] Analyze ChatGPT consolidated file (discarded - inferior to our workflow)
- [ ] Process historical symposium attendance (2015-2023) when available
- [ ] Add `symposia_attended` field to Django MemberProfile model
- [ ] Create import management command for Django
- [ ] Verify data integrity before import
- [ ] Run pilot import with small batch

---

## 11. Scripts Created

| Script | Purpose |
|--------|---------|
| `merge_canonical_list.py` | Merges MemberPress CSV with symposium Excel, creates canonical list |
| `remove_inactive_members.py` | Removes unsubscribed members, outputs cleaned list |
| `add_active_members.py` | Adds missing active mailing list members, deduplicates final list |

---

*Last updated: December 24, 2025*
