# Contributor Statistics Section - Design Document

**Goal:** Thêm section mới hiển thị bảng thống kê chi tiết metrics cho từng contributor/user.

**Architecture:** Mở rộng `pr_analyzer.py` để tính toán stats theo user, thêm UI section mới trong `app.py` sử dụng Streamlit dataframe cho interactive table.

**Tech Stack:** Python, Streamlit, pandas, PyGithub

---

## Table Columns

| Cột | Mô tả | Tính toán |
|-----|-------|-----------|
| **Username** | Tên user | `pr.user.login` |
| **Total PRs** | Tổng số PRs | Count by user |
| **Merged** | Số PRs đã merge | Count where `merged_at is not None` |
| **Open** | Số PRs đang open | Count where `state == 'open'` |
| **Closed** | Số PRs closed (không merge) | Count where `state == 'closed' and merged_at is None` |
| **Merge Rate %** | Tỷ lệ merge thành công | `(Merged / Total) * 100` |
| **Avg Merge Time** | Thờ gian trung bình open -> merge | Average of `(merged_at - created_at)` |
| **AI PRs** | Số PRs là AI-generated | Count where `is_ai_pr(pr) == True` |
| **PRs/Week** | Tần suất tạo PR | `Total PRs / (date_range_in_weeks)` |
| **Comments/PR** | Trung bình comments/PR | Lazy loaded via separate API call |

## UI/UX Design

### Section Layout
```
## Contributor Statistics
[Button: Load Comments]  <- Only visible if comments not loaded

| Username | Total | Merged | Open | Closed | Merge Rate | Avg Merge Time | AI PRs | PRs/Week | Comments/PR |
|----------|-------|--------|------|--------|------------|----------------|--------|----------|-------------|
| user1    | 15    | 12     | 2    | 1      | 80.0%      | 24.5h          | 3      | 3.75     | -           |
| user2    | 8     | 6      | 1    | 1      | 75.0%      | 18.2h          | 0      | 2.0      | 5.2         |
```

### Features
- **Sorting:** Mặc định theo Total PRs giảm dần
- **Lazy Loading Comments:** Nút "Load Comments" để fetch comments count cho tất cả PRs
- **Interactive:** Có thể click column header để sort

## Data Flow

```
prs (List[PullRequest])
    |
    v
analyze_contributors(prs) -> Dict[str, ContributorStats]
    |
    v
DataFrame -> st.dataframe()
    |
    v
[User clicks Load Comments]
    |
    v
fetch_comments_for_prs(prs) -> Update DataFrame
```

## Error Handling

| Scenario | Xử lý |
|----------|-------|
| API rate limit khi load comments | Hiển thị warning, cho phép retry |
| PR không có comments | Hiển thị "0" |
| User không có merged PRs | Avg Merge Time = "N/A" |

## Testing Strategy

- Unit test cho `analyze_contributors()`
- Test lazy loading comments
- Test edge cases (user có 0 PRs, user chỉ có AI PRs, etc.)
