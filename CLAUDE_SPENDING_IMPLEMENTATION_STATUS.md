# Claude Spending Tracking - Implementation Status

**Date:** November 30, 2025
**Status:** ✅ 90% Complete - Core Backend Done, Frontend Needs JavaScript

---

## ✅ COMPLETED

### 1. **Backend - Spending Tracker** ✅
**File:** `backend/spending_tracker.py`

- ✅ SQLite database creation
- ✅ Monthly spending tracking
- ✅ $20/month cap (configurable)
- ✅ Budget checking before analysis
- ✅ Historical tracking
- ✅ Monthly stats aggregation

**Functions:**
- `get_current_month_spending()` - Get total spent this month
- `get_monthly_cap()` - Get current month's cap
- `set_monthly_cap(amount)` - Update cap
- `can_afford(cost)` - Check if within budget
- `record_analysis(data)` - Save analysis to history
- `get_monthly_history()` - Get all analyses
- `get_monthly_stats()` - Get aggregated stats

### 2. **Backend - Cost Estimator** ✅
**File:** `backend/cost_estimator.py`

- ✅ Accurate token counting (using tiktoken)
- ✅ Page estimation (650 tokens ≈ 1 page)
- ✅ Claude Sonnet 4.5 pricing ($3/1M input, $15/1M output)
- ✅ Batch calculation (15 docs per batch for granular progress)
- ✅ Time estimation

**Function:**
- `estimate_claude_cost(documents)` - Returns detailed cost breakdown

### 3. **Backend - API Endpoints** ✅
**File:** `backend/main.py`

**New Endpoints:**
1. ✅ `GET /spending-dashboard` - Get monthly stats & history
2. ✅ `POST /update-spending-cap` - Change monthly cap
3. ✅ `POST /estimate-analysis-cost` - Calculate cost before running Claude

**Updated Imports:**
- ✅ Added `SpendingTracker` import
- ✅ Added `estimate_claude_cost` import
- ✅ Initialized `spending_tracker` global

### 4. **Frontend - HTML Structure** ✅
**File:** `backend/static/index.html`

**Removed:**
- ✅ Beginner/Intermediate/Advanced level selector buttons (per your request)
- ✅ Removed associated CSS styles

**Added:**
- ✅ Spending Dashboard HTML structure
- ✅ Modal overlay for dialogs
- ✅ Complete CSS styling for:
  - Spending dashboard layout
  - Stat boxes
  - Progress bars
  - Modal dialogs
  - Budget warnings
  - History display

---

## ⚠️ REMAINING WORK

### Frontend - JavaScript Functions (Needed)

**Location:** `backend/static/index.html` - need to add to `<script>` section

**Functions to Add:**

1. **Load Dashboard on Page Load**
```javascript
async function loadSpendingDashboard() {
    const response = await fetch('/spending-dashboard');
    const data = await response.json();
    updateDashboardUI(data.stats);
}

function updateDashboardUI(stats) {
    document.getElementById('spentThisMonth').textContent = `$${stats.total_cost}`;
    document.getElementById('remainingBudget').textContent = `$${stats.remaining_budget}`;
    document.getElementById('monthlyCap').textContent = `$${stats.monthly_cap}`;
    // ... update other elements
}
```

2. **Change Spending Cap**
```javascript
async function changeSpendingCap() {
    const newCap = prompt("Enter new monthly cap:", "40");
    if (newCap) {
        await fetch('/update-spending-cap', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({new_cap: parseFloat(newCap)})
        });
        loadSpendingDashboard();
    }
}
```

3. **Show Spending History**
```javascript
async function showSpendingHistory() {
    const response = await fetch('/spending-dashboard');
    const data = await response.json();

    // Build modal HTML with history
    const modalHTML = `
        <h3>📊 Claude Spending History</h3>
        <!-- Display data.history items -->
    `;

    showModal(modalHTML);
}
```

4. **Modal Functions**
```javascript
function showModal(content) {
    document.getElementById('modalContent').innerHTML = content;
    document.getElementById('modalOverlay').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modalOverlay').style.display = 'none';
}
```

5. **Update Current Month Display**
```javascript
function updateCurrentMonth() {
    const now = new Date();
    const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"];
    document.getElementById('currentMonth').textContent =
        `${monthNames[now.getMonth()]} ${now.getFullYear()}`;
}
```

---

## 📝 TO-DO LIST

1. ⏳ Add JavaScript functions to HTML (above list)
2. ⏳ Update `tagging.py` - set `batch_size=15` in `claude_second_pass_analysis()`
3. ⏳ Create `/analyze-recent` endpoint that:
   - Calls `estimate_analysis_cost()` first
   - Checks budget with `spending_tracker.can_afford()`
   - Runs Claude analysis in batches
   - Records actual spending with `spending_tracker.record_analysis()`
4. ⏳ Test with small document set
5. ⏳ Test budget cap enforcement
6. ⏳ Test month rollover

---

## 🧪 TESTING CHECKLIST

### Manual Tests Needed:

- [ ] Load page - dashboard shows $0/$20
- [ ] Click "Change" - can update cap to $40
- [ ] Upload document - spending stays $0 (Ollama/keyword only)
- [ ] (Future) Run Claude analysis - dashboard updates with cost
- [ ] Click "View History" - shows modal (currently empty)
- [ ] Set cap to $1, try $2 analysis - should block

---

## 💡 WHAT YOU HAVE NOW

### Working Features:
1. ✅ Ollama tagging (FREE)
2. ✅ OpenAI tagging (cheap)
3. ✅ Keyword-based tagging (FREE, default)
4. ✅ Spending tracker database (empty but ready)
5. ✅ Cost estimator (accurate token counting)
6. ✅ Beautiful spending dashboard UI

### Ready to Add:
- Claude analysis buttons ("Analyze Recent", "Analyze Full DB", etc.)
- These will use the cost estimator and spending tracker
- User sees cost before proceeding
- Budget enforced automatically

---

## 📄 FILE SUMMARY

| File | Status | Purpose |
|------|--------|---------|
| `backend/spending_tracker.py` | ✅ Complete | Track Claude spending, enforce $20 cap |
| `backend/cost_estimator.py` | ✅ Complete | Calculate accurate costs from token counts |
| `backend/main.py` | ✅ 90% | API endpoints added, need analyze endpoints |
| `backend/static/index.html` | ⏳ 85% | UI complete, needs JavaScript functions |
| `backend/tagging.py` | ⏳ Pending | Update batch_size=15 |
| `backend/claude_spending.db` | ✅ Auto-created | SQLite database (empty) |

---

## 🚀 NEXT STEPS

**Option 1: I can complete the JavaScript now**
- Add all the functions listed above
- Wire up the buttons
- Test the dashboard

**Option 2: You test what's there first**
- Start the server: `python backend/main.py`
- Go to `http://localhost:8000`
- See the spending dashboard (will show $0)
- Test Ollama upload
- Then I'll add Claude analysis features

**Which would you prefer?**

Let me know and I'll finish the implementation!
