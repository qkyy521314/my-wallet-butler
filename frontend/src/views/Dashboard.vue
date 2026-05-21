<template>
  <div class="dashboard">
    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card stat-card--assets stagger-1">
        <div class="stat-card__icon stat-card__icon--teal">
          <el-icon><Wallet /></el-icon>
        </div>
        <div class="stat-card__content">
          <span class="stat-card__label">总资产</span>
          <span class="stat-card__value">¥ {{ formatMoney(totalAssets) }}</span>
          <span class="stat-card__trend stat-card__trend--up">
            <el-icon><TrendCharts /></el-icon>
            +12.5%
          </span>
        </div>
      </div>

      <div class="stat-card stat-card--income stagger-2">
        <div class="stat-card__icon stat-card__icon--green">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-card__content">
          <span class="stat-card__label">本月收入</span>
          <span class="stat-card__value">¥ {{ formatMoney(monthlyIncome) }}</span>
          <span class="stat-card__trend stat-card__trend--up">
            <el-icon><Top /></el-icon>
            +8.2%
          </span>
        </div>
      </div>

      <div class="stat-card stat-card--expense stagger-3">
        <div class="stat-card__icon stat-card__icon--red">
          <el-icon><Bottom /></el-icon>
        </div>
        <div class="stat-card__content">
          <span class="stat-card__label">本月支出</span>
          <span class="stat-card__value">¥ {{ formatMoney(monthlyExpense) }}</span>
          <span class="stat-card__trend stat-card__trend--down">
            <el-icon><Bottom /></el-icon>
            -3.1%
          </span>
        </div>
      </div>

      <div class="stat-card stat-card--balance stagger-4">
        <div class="stat-card__icon stat-card__icon--amber">
          <el-icon><Coin /></el-icon>
        </div>
        <div class="stat-card__content">
          <span class="stat-card__label">本月结余</span>
          <span class="stat-card__value" :class="balanceClass">¥ {{ formatMoney(balance) }}</span>
          <span class="stat-card__trend" :class="balance >= 0 ? 'stat-card__trend--up' : 'stat-card__trend--down'">
            <el-icon><CaretTop v-if="balance >= 0" /><CaretBottom v-else /></el-icon>
            {{ balance >= 0 ? '盈余' : '亏损' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="dashboard-grid">
      <!-- Recent Transactions -->
      <el-card class="dashboard-card dashboard-card--transactions animate-slide-up stagger-5">
        <template #header>
          <div class="card-header">
            <div class="card-header__left">
              <el-icon class="card-header__icon"><Clock /></el-icon>
              <span>最近交易</span>
            </div>
            <el-button type="primary" text @click="$router.push('/transactions')">
              查看全部
              <el-icon class="card-header__arrow"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>

        <div class="transactions-list">
          <div
            v-for="(transaction, index) in recentTransactions"
            :key="transaction.id"
            class="transaction-item"
            :class="`stagger-${index + 1}`"
          >
            <div class="transaction-item__icon" :class="getTransactionIconClass(transaction.amount)">
              <el-icon>
                <ShoppingCart v-if="transaction.amount < 0 && getCategoryType(transaction.category?.name) === 'expense'" />
                <Money v-else-if="transaction.amount > 0" />
                <Switch v-else />
              </el-icon>
            </div>
            <div class="transaction-item__info">
              <span class="transaction-item__desc">{{ transaction.description }}</span>
              <span class="transaction-item__category">{{ transaction.category?.name || '未分类' }}</span>
            </div>
            <div class="transaction-item__amount" :class="transaction.amount > 0 ? 'positive' : 'negative'">
              {{ transaction.amount > 0 ? '+' : '' }}¥ {{ formatMoney(Math.abs(transaction.amount)) }}
            </div>
          </div>

          <el-empty v-if="recentTransactions.length === 0" description="暂无交易记录" :image-size="80" />
        </div>
      </el-card>

      <!-- Account Balances -->
      <el-card class="dashboard-card dashboard-card--accounts animate-slide-up stagger-6">
        <template #header>
          <div class="card-header">
            <div class="card-header__left">
              <el-icon class="card-header__icon"><CreditCard /></el-icon>
              <span>账户余额</span>
            </div>
            <el-button type="primary" text @click="$router.push('/accounts')">
              管理账户
              <el-icon class="card-header__arrow"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>

        <div class="accounts-list">
          <div
            v-for="(account, index) in accountBalances"
            :key="index"
            class="account-item"
            :class="`stagger-${index + 1}`"
          >
            <div class="account-item__icon">
              <el-icon><Wallet /></el-icon>
            </div>
            <div class="account-item__info">
              <span class="account-item__name">{{ account.name }}</span>
              <span class="account-item__type">{{ account.type || '主账户' }}</span>
            </div>
            <div class="account-item__balance">
              ¥ {{ formatMoney(account.balance) }}
            </div>
          </div>

          <el-empty v-if="accountBalances.length === 0" description="暂无账户" :image-size="80" />
        </div>

        <div class="accounts-summary">
          <div class="summary-item">
            <span class="summary-label">总资产</span>
            <span class="summary-value">¥ {{ formatMoney(totalAssets) }}</span>
          </div>
        </div>
      </el-card>

      <!-- Quick Actions -->
      <el-card class="dashboard-card dashboard-card--actions animate-slide-up stagger-7">
        <template #header>
          <div class="card-header">
            <div class="card-header__left">
              <el-icon class="card-header__icon"><Lightning /></el-icon>
              <span>快捷操作</span>
            </div>
          </div>
        </template>

        <div class="quick-actions">
          <div class="quick-action" @click="handleQuickAction('income')">
            <div class="quick-action__icon quick-action__icon--income">
              <el-icon><Plus /></el-icon>
            </div>
            <span>记收入</span>
          </div>
          <div class="quick-action" @click="handleQuickAction('expense')">
            <div class="quick-action__icon quick-action__icon--expense">
              <el-icon><Minus /></el-icon>
            </div>
            <span>记支出</span>
          </div>
          <div class="quick-action" @click="handleQuickAction('transfer')">
            <div class="quick-action__icon quick-action__icon--transfer">
              <el-icon><Switch /></el-icon>
            </div>
            <span>转账</span>
          </div>
          <div class="quick-action" @click="handleQuickAction('export')">
            <div class="quick-action__icon quick-action__icon--export">
              <el-icon><Download /></el-icon>
            </div>
            <span>导出</span>
          </div>
        </div>
      </el-card>

      <!-- Budget Overview -->
      <el-card class="dashboard-card dashboard-card--budget animate-slide-up stagger-8">
        <template #header>
          <div class="card-header">
            <div class="card-header__left">
              <el-icon class="card-header__icon"><PieChart /></el-icon>
              <span>预算进度</span>
            </div>
            <el-button type="primary" text @click="$router.push('/budgets')">
              详细
              <el-icon class="card-header__arrow"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>

        <div class="budget-items">
          <div class="budget-item" v-for="(budget, index) in budgetOverview" :key="index">
            <div class="budget-item__header">
              <span class="budget-item__name">{{ budget.category }}</span>
              <span class="budget-item__percent">{{ budget.percent }}%</span>
            </div>
            <el-progress
              :percentage="budget.percent"
              :color="budget.percent > 80 ? '#EF4444' : budget.percent > 60 ? '#F59E0B' : '#0D9488'"
              :show-text="false"
              :stroke-width="8"
              class="budget-progress"
            />
            <div class="budget-item__footer">
              <span>¥ {{ formatMoney(budget.spent) }}</span>
              <span>/ ¥ {{ formatMoney(budget.limit) }}</span>
            </div>
          </div>

          <el-empty v-if="budgetOverview.length === 0" description="暂无预算设置" :image-size="80" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Wallet,
  TrendCharts,
  Top,
  Bottom,
  Coin,
  CaretTop,
  CaretBottom,
  Clock,
  ArrowRight,
  CreditCard,
  Lightning,
  Plus,
  Minus,
  Switch,
  Download,
  ShoppingCart,
  Money,
  PieChart
} from '@element-plus/icons-vue'
import { useAccountStore } from '@/store/modules/account'

const router = useRouter()
const accountStore = useAccountStore()

const totalAssets = ref(15420.50)
const monthlyIncome = ref(8500.00)
const monthlyExpense = ref(3240.75)
const balance = computed(() => monthlyIncome.value - monthlyExpense.value)

const balanceClass = computed(() => balance.value >= 0 ? 'positive' : 'negative')

const recentTransactions = ref([
  { id: 1, description: '工资收入', amount: 8500.00, date: '2023-05-15T00:00:00Z', category: { name: '工资' } },
  { id: 2, description: '超市购物', amount: -245.50, date: '2023-05-14T00:00:00Z', category: { name: '食品' } },
  { id: 3, description: '餐厅用餐', amount: -120.00, date: '2023-05-13T00:00:00Z', category: { name: '餐饮' } },
  { id: 4, description: '房租支付', amount: -2000.00, date: '2023-05-01T00:00:00Z', category: { name: '住房' } },
])

const accountBalances = ref([
  { name: '现金', type: '现金', balance: 2340.50 },
  { name: '建设银行', type: '储蓄卡', balance: 8540.00 },
  { name: '支付宝', type: '电子钱包', balance: 4540.00 },
])

const budgetOverview = ref([
  { category: '餐饮', spent: 1250, limit: 2000, percent: 62 },
  { category: '购物', spent: 850, limit: 1500, percent: 57 },
  { category: '交通', spent: 320, limit: 500, percent: 64 },
  { category: '娱乐', spent: 280, limit: 800, percent: 35 },
])

const formatMoney = (value: number) => {
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const getCategoryType = (categoryName: string | undefined) => {
  if (!categoryName) return 'expense'
  const incomeCategories = ['工资', '奖金', '投资收益', '其他收入']
  return incomeCategories.includes(categoryName) ? 'income' : 'expense'
}

const getTransactionIconClass = (amount: number) => {
  return amount > 0 ? 'icon--income' : 'icon--expense'
}

const handleQuickAction = (type: string) => {
  router.push(`/transactions?action=${type}`)
}

onMounted(async () => {
  await accountStore.fetchAccounts()
  if (accountStore.accounts.length > 0) {
    accountBalances.value = accountStore.accounts.map((account: any) => ({
      name: account.name,
      type: account.type || '主账户',
      balance: account.balance
    }))
    totalAssets.value = accountStore.accounts.reduce((sum: number, acc: any) => sum + (acc.balance || 0), 0)
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.dashboard {
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $space-lg;
  margin-bottom: $space-xl;
}

.stat-card {
  background: white;
  border-radius: $radius-lg;
  padding: $space-lg;
  display: flex;
  align-items: flex-start;
  gap: $space-md;
  box-shadow: $shadow-card;
  transition: all $transition-base;
  border: 1px solid $border-light;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    opacity: 0;
    transition: opacity $transition-base;
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-card-hover;

    &::before {
      opacity: 1;
    }
  }

  &--assets::before {
    background: linear-gradient(90deg, $primary-color, $primary-light);
  }

  &--income::before {
    background: linear-gradient(90deg, $success-color, lighten($success-color, 10%));
  }

  &--expense::before {
    background: linear-gradient(90deg, $danger-color, lighten($danger-color, 10%));
  }

  &--balance::before {
    background: linear-gradient(90deg, $warning-color, lighten($warning-color, 10%));
  }

  &__icon {
    width: 52px;
    height: 52px;
    border-radius: $radius-md;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;

    &--teal {
      background: rgba($primary-color, 0.1);
      color: $primary-color;
    }

    &--green {
      background: rgba($success-color, 0.1);
      color: $success-color;
    }

    &--red {
      background: rgba($danger-color, 0.1);
      color: $danger-color;
    }

    &--amber {
      background: rgba($warning-color, 0.1);
      color: $warning-color;
    }
  }

  &__content {
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  &__label {
    font-size: $text-sm;
    color: $text-secondary;
    margin-bottom: $space-xs;
  }

  &__value {
    font-family: $font-display;
    font-size: $text-2xl;
    font-weight: 700;
    color: $text-primary;
    line-height: 1.2;
  }

  &__trend {
    display: flex;
    align-items: center;
    gap: 2px;
    font-size: $text-xs;
    font-weight: 500;
    margin-top: $space-xs;

    &--up {
      color: $success-color;
    }

    &--down {
      color: $danger-color;
    }

    .el-icon {
      font-size: 12px;
    }
  }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $space-lg;
}

.dashboard-card {
  &--transactions,
  &--accounts {
    grid-row: span 2;
  }

  :deep(.el-card__header) {
    padding: $space-md $space-lg;
    border-bottom: 1px solid $border-light;
  }

  :deep(.el-card__body) {
    padding: $space-md;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  &__left {
    display: flex;
    align-items: center;
    gap: $space-sm;
    font-family: $font-display;
    font-weight: 600;
    font-size: $text-base;
    color: $text-primary;
  }

  &__icon {
    font-size: 18px;
    color: $primary-color;
  }

  &__arrow {
    margin-left: 4px;
    font-size: 14px;
  }

  :deep(.el-button--text) {
    display: flex;
    align-items: center;
    gap: 4px;
    color: $primary-color;
    font-weight: 500;
  }
}

// Transactions List
.transactions-list {
  display: flex;
  flex-direction: column;
}

.transaction-item {
  display: flex;
  align-items: center;
  padding: $space-md;
  border-radius: $radius-md;
  transition: background-color $transition-fast;

  &:hover {
    background-color: $gray-50;
  }

  &__icon {
    width: 40px;
    height: 40px;
    border-radius: $radius-md;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    margin-right: $space-md;
    flex-shrink: 0;

    &.icon--income {
      background: rgba($success-color, 0.1);
      color: $success-color;
    }

    &.icon--expense {
      background: rgba($danger-color, 0.1);
      color: $danger-color;
    }
  }

  &__info {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  &__desc {
    font-weight: 500;
    color: $text-primary;
    font-size: $text-base;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__category {
    font-size: $text-xs;
    color: $text-tertiary;
  }

  &__amount {
    font-family: $font-display;
    font-weight: 600;
    font-size: $text-base;
    margin-left: $space-md;
    flex-shrink: 0;

    &.positive {
      color: $success-color;
    }

    &.negative {
      color: $text-primary;
    }
  }
}

// Accounts List
.accounts-list {
  display: flex;
  flex-direction: column;
}

.account-item {
  display: flex;
  align-items: center;
  padding: $space-md;
  border-radius: $radius-md;
  transition: background-color $transition-fast;

  &:hover {
    background-color: $gray-50;
  }

  &__icon {
    width: 40px;
    height: 40px;
    border-radius: $radius-md;
    background: linear-gradient(135deg, $primary-color 0%, $primary-light 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    margin-right: $space-md;
    flex-shrink: 0;
  }

  &__info {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  &__name {
    font-weight: 500;
    color: $text-primary;
    font-size: $text-base;
  }

  &__type {
    font-size: $text-xs;
    color: $text-tertiary;
  }

  &__balance {
    font-family: $font-display;
    font-weight: 600;
    font-size: $text-base;
    color: $text-primary;
    margin-left: $space-md;
    flex-shrink: 0;
  }
}

.accounts-summary {
  margin-top: $space-md;
  padding-top: $space-md;
  border-top: 1px solid $border-light;
  display: flex;
  justify-content: space-between;

  .summary-item {
    display: flex;
    justify-content: space-between;
    width: 100%;
    padding: $space-sm $space-md;
  }

  .summary-label {
    font-weight: 500;
    color: $text-secondary;
    font-size: $text-sm;
  }

  .summary-value {
    font-family: $font-display;
    font-weight: 600;
    color: $primary-color;
    font-size: $text-base;
  }
}

// Quick Actions
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $space-md;
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $space-sm;
  padding: $space-lg $space-md;
  border-radius: $radius-lg;
  cursor: pointer;
  transition: all $transition-base;
  border: 1px solid transparent;

  &:hover {
    background-color: $gray-50;
    border-color: $border-color;
    transform: translateY(-2px);
  }

  &__icon {
    width: 48px;
    height: 48px;
    border-radius: $radius-md;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;

    &--income {
      background: rgba($success-color, 0.1);
      color: $success-color;
    }

    &--expense {
      background: rgba($danger-color, 0.1);
      color: $danger-color;
    }

    &--transfer {
      background: rgba($info-color, 0.1);
      color: $info-color;
    }

    &--export {
      background: rgba($primary-color, 0.1);
      color: $primary-color;
    }
  }

  span {
    font-size: $text-sm;
    font-weight: 500;
    color: $text-secondary;
  }
}

// Budget Items
.budget-items {
  display: flex;
  flex-direction: column;
  gap: $space-lg;
}

.budget-item {
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $space-sm;
  }

  &__name {
    font-weight: 500;
    color: $text-primary;
    font-size: $text-sm;
  }

  &__percent {
    font-family: $font-display;
    font-weight: 600;
    font-size: $text-sm;
    color: $text-secondary;
  }

  .budget-progress {
    margin-bottom: $space-xs;

    :deep(.el-progress-bar__outer) {
      background-color: $gray-100;
    }
  }

  &__footer {
    display: flex;
    justify-content: space-between;
    font-size: $text-xs;
    color: $text-tertiary;

    span:first-child {
      font-weight: 500;
      color: $text-secondary;
    }
  }
}

// Animation
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-up {
  animation: slideUp 0.5s ease forwards;
  opacity: 0;
}

// Responsive
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-card--transactions,
  .dashboard-card--accounts {
    grid-row: span 1;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-card {
    flex-direction: column;
    text-align: center;

    &__icon {
      margin: 0 auto;
    }

    &__content {
      align-items: center;
    }
  }
}
</style>
