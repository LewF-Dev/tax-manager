# Tax Manager UI - Visual Preview

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ Tax Manager          user@example.com  [Active]  [Logout]   │ ← Top Bar
├──────────┬──────────────────────────────────────────────────┤
│          │                                                   │
│ Dashboard│  Status                                          │
│ Income   │  ┌──────────────────────────────────────────┐   │
│ Expenses │  │ Current tax year: 2024-25                │   │
│ Tax      │  │ Universal Credit: Enabled                │   │
│ UC       │  │ Subscription: Active                     │   │
│          │  └──────────────────────────────────────────┘   │
│ Settings │                                                   │
│ Exports  │  This Tax Year                                   │
│          │  ┌──────────┬──────────┬──────────┐             │
│          │  │ Income   │ Tax Set  │ Est. Tax │             │
│          │  │ £15,000  │ £3,750   │ £179     │             │
│          │  └──────────┴──────────┴──────────┘             │
│          │                                                   │
│          │  Next Actions                                    │
│          │  ┌──────────────────────────────────────────┐   │
│          │  │ • UC report due in 6 days                │   │
│          │  │ • HMRC deadline: 245 days                │   │
│          │  └──────────────────────────────────────────┘   │
│          │                                                   │
└──────────┴──────────────────────────────────────────────────┘
```

## Dashboard

**Philosophy: Task clarity, not stats**

```
Status
┌─────────────────────────────────────┐
│ Current tax year      2024-25       │
│ Universal Credit      Enabled       │
│ Subscription          Active        │
│ Trading since         01 June 2024  │
└─────────────────────────────────────┘

This Tax Year
┌──────────────┬──────────────┬──────────────┐
│ Total Income │ Tax Set Aside│ Estimated Tax│
│   £15,000.00 │    £3,750.00 │     £179.40  │
└──────────────┴──────────────┴──────────────┘

Universal Credit
┌─────────────────────────────────────┐
│ Current Period: 15 Jun - 14 Jul     │ [Not Reported]
│ Income: £1,500  Expenses: £150      │
│ Net Profit: £1,350                  │
└─────────────────────────────────────┘

Next Actions
┌─────────────────────────────────────┐
│ • UC report due in 6 days           │
│ • HMRC deadline: 245 days           │
│ • No income recorded this month     │
└─────────────────────────────────────┘

[Add Income]  [Add Expense]
```

## Income Page

**Philosophy: Form-first, fast entry**

```
Add Income
┌─────────────────────────────────────────────────┐
│ Date Received  [2024-12-25▼]                    │
│ Amount (£)     [0.00        ]                   │
│ Description    [e.g., Website development...]   │
│                                [Add Income]      │
└─────────────────────────────────────────────────┘

Remember: Set aside 20% of each payment for tax.
For your last payment of £1,500.00, that's £300.00.

Income History                    Total: £15,000.00
┌──────────┬─────────────────┬──────────┬─────────┬────────┐
│ Date     │ Description     │ Amount   │ Tax Year│ Actions│
├──────────┼─────────────────┼──────────┼─────────┼────────┤
│ 15 Jun   │ Website project │ £1,500.00│ 2024-25 │ Delete │
│ 01 Jun   │ Consulting work │ £2,000.00│ 2024-25 │ Delete │
└──────────┴─────────────────┴──────────┴─────────┴────────┘
```

## Expenses Page

**Philosophy: Same as income, with categories**

```
Add Expense
┌─────────────────────────────────────────────────┐
│ Date Paid      [2024-12-25▼]                    │
│ Amount (£)     [0.00        ]                   │
│ Category       [Select...   ▼]                  │
│ Description    [e.g., Adobe Creative Cloud...]  │
│                                [Add Expense]     │
└─────────────────────────────────────────────────┘

Expense History                   Total: £2,500.00
┌──────────┬──────────┬─────────────┬─────────┬─────────┬────────┐
│ Date     │ Category │ Description │ Amount  │ Tax Year│ Actions│
├──────────┼──────────┼─────────────┼─────────┼─────────┼────────┤
│ 10 Jun   │ Software │ Adobe CC    │ £49.99  │ 2024-25 │ Delete │
│ 05 Jun   │ Equipment│ New laptop  │ £800.00 │ 2024-25 │ Delete │
└──────────┴──────────┴─────────────┴─────────┴─────────┴────────┘
```

## Tax Page

**Philosophy: Transparent calculations, no hidden logic**

```
Tax Year 2024-25 runs from 06 April 2024 to 05 April 2025.
This is an estimate based on current HMRC rules.

Income & Expenses          Estimated Tax
┌──────────────────────┐  ┌──────────────────────┐
│ Total Income         │  │ Income Tax           │
│ £15,000.00           │  │ £0.00                │
│                      │  │                      │
│ Total Expenses       │  │ NI Class 2           │
│ £2,500.00            │  │ £179.40              │
│                      │  │                      │
│ Net Profit           │  │ NI Class 4           │
│ £12,500.00           │  │ £0.00                │
│                      │  │                      │
│                      │  │ Total Tax            │
│                      │  │ £179.40              │
└──────────────────────┘  └──────────────────────┘

Tax to Set Aside
┌─────────────────────────────────────────────────┐
│ Based on 20% of income           £3,750.00      │
│                                                  │
│ You're setting aside more than estimated tax,   │
│ which provides a buffer.                        │
└─────────────────────────────────────────────────┘

▼ How This is Calculated
┌─────────────────────────────────────────────────┐
│ Income Tax                                       │
│ Based on your net profit of £12,500.00:         │
│ • Personal Allowance: £12,570 (tax-free)        │
│ • Basic rate (20%): £12,571 - £50,270           │
│ • Higher rate (40%): £50,271 - £125,140         │
│                                                  │
│ National Insurance Class 2                      │
│ Flat weekly rate of £3.45 (£179.40 per year)    │
│ if profits exceed £6,725.                       │
│                                                  │
│ National Insurance Class 4                      │
│ Based on profits:                                │
│ • 9% on profits between £12,570 and £50,270     │
│ • 2% on profits over £50,270                    │
└─────────────────────────────────────────────────┘

HMRC Registration
┌─────────────────────────────────────────────────┐
│ Trading started        01 June 2024             │
│ Registration deadline  05 October 2025          │
│ Days remaining         245 days                 │
└─────────────────────────────────────────────────┘

VAT Registration
┌─────────────────────────────────────────────────┐
│ Current turnover       £15,000.00               │
│ [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 17.6%       │
│ £0                                    £85,000   │
│                                                  │
│ You're 17.6% of the way to the £85,000 VAT     │
│ threshold.                                       │
└─────────────────────────────────────────────────┘
```

## Universal Credit Page

**Philosophy: Separate, clear, no cross-contamination**

```
How UC Reporting Works
┌─────────────────────────────────────────────────┐
│ • Report income and expenses on cash-received   │
│   basis                                          │
│ • Your assessment period runs from the 15th     │
│ • Only report money actually received or paid   │
│ • £0 months must still be reported              │
└─────────────────────────────────────────────────┘

Current Assessment Period
┌─────────────────────────────────────────────────┐
│ 15 June 2024 - 14 July 2024    [Not Reported]  │
│                                                  │
│ Income          Expenses        Net Profit      │
│ £1,500.00       £150.00         £1,350.00       │
│                                                  │
│ After reporting to UC, mark as reported:        │
│ [2024-12-25▼]  [Mark as Reported]              │
└─────────────────────────────────────────────────┘

Previous Periods
┌──────────────────┬─────────┬──────────┬──────────┬────────┐
│ Period           │ Income  │ Expenses │ Net      │ Status │
├──────────────────┼─────────┼──────────┼──────────┼────────┤
│ 15 May - 14 Jun  │ £2,000  │ £200     │ £1,800   │ ✓ Rep. │
│ 15 Apr - 14 May  │ £0      │ £0       │ £0       │ ✓ Rep. │
└──────────────────┴─────────┴──────────┴──────────┴────────┘

Important
• These figures are for your records only
• You must report to UC separately via your UC account
• This app does not communicate with Universal Credit
```

## Settings Page

**Philosophy: Control and transparency**

```
Profile
┌─────────────────────────────────────────────────┐
│ Full Name      [John Smith                   ]  │
│ Email          [user@example.com] (read-only)   │
│                                [Save Profile]    │
└─────────────────────────────────────────────────┘

Trading Configuration
┌─────────────────────────────────────────────────┐
│ Trading Start Date  [2024-06-01▼]               │
│ Tax Set Aside %     [20] %                      │
│                                [Save Settings]   │
└─────────────────────────────────────────────────┘

Universal Credit
┌─────────────────────────────────────────────────┐
│ ☑ Enable Universal Credit reporting             │
│ Assessment Day      [15] of each month          │
│                                [Save UC Settings]│
└─────────────────────────────────────────────────┘

Subscription
┌─────────────────────────────────────────────────┐
│ Status: Active                                   │
│                        [Manage Subscription]     │
└─────────────────────────────────────────────────┘

Danger Zone
┌─────────────────────────────────────────────────┐
│ Delete Account                                   │
│ Permanently delete your account and all data.   │
│ This cannot be undone. Export data first.       │
│                        [Delete Account]          │
└─────────────────────────────────────────────────┘
```

## Exports Page

**Philosophy: Data portability, trust**

```
Transaction Export (CSV)
┌─────────────────────────────────────────────────┐
│ Download all income and expense transactions    │
│ in CSV format. Suitable for spreadsheets.      │
│                                                  │
│ Includes: Date, Type, Amount, Description       │
│                            [Download CSV]        │
└─────────────────────────────────────────────────┘

Full Data Export (JSON)
┌─────────────────────────────────────────────────┐
│ Download all your data in JSON format.          │
│ Includes profile, transactions, UC reports,     │
│ and tax snapshots. Required for GDPR.           │
│                                                  │
│ Includes: Everything                            │
│                            [Download JSON]       │
└─────────────────────────────────────────────────┘

About Data Exports
• Exports contain all your data up to now
• CSV format is best for spreadsheets
• JSON format contains complete data
• Exports are generated in real-time
• Your data is never shared with third parties

Data Portability
You own your data. You can export it at any time,
for any reason. If you decide to leave, you can
take everything with you.
```

## Color Palette

```
Background:     #F9FAFB (gray-50)
Cards:          #FFFFFF (white)
Borders:        #E5E7EB (gray-200)
Text Primary:   #111827 (gray-900)
Text Secondary: #6B7280 (gray-600)
Accent:         #2563EB (blue-600)
Success:        #10B981 (green-500)
Warning:        #F59E0B (yellow-500)
Danger:         #EF4444 (red-500)
```

## Typography

```
Headings:       font-semibold, text-2xl/xl/lg
Body:           text-sm/base
Labels:         text-sm, font-medium
Numbers:        monospace (Courier New)
```

## Spacing

```
Page padding:   p-8
Card padding:   p-6
Form spacing:   space-y-4
Grid gaps:      gap-4/6
```

## Responsive Behavior

### Desktop (>768px)
- Sidebar visible
- Multi-column grids
- Full tables

### Mobile (<768px)
- Sidebar becomes top tabs
- Single column layout
- Tables scroll horizontally
- Forms stack vertically

## What You DON'T See

❌ No charts
❌ No graphs
❌ No progress bars (except VAT threshold)
❌ No animations
❌ No tooltips
❌ No modals
❌ No notifications (yet)
❌ No loading spinners (yet)
❌ No decorative icons
❌ No gamification
❌ No "insights"
❌ No "recommendations"

## What You DO See

✅ Clear status
✅ Key numbers
✅ Next actions
✅ Simple forms
✅ Boring tables
✅ Transparent calculations
✅ Plain language
✅ Delete button in plain sight

## Philosophy in Every Pixel

**Boring**: No visual tricks
**Predictable**: Same layout everywhere
**Opinionated**: One way to do things
**Transparent**: Show the logic
**Honest**: No dark patterns
**Respectful**: User owns their data

This is what a finance app looks like when it's designed for adults who want control, not motivation.
