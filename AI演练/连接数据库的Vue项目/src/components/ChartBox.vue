<template>
  <div ref="chartRef" class="chart-box" :style="{ height: height }"></div>
</template>

<script setup>
import { ref, shallowRef, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: String, default: '320px' }
})

const chartRef = ref(null)
const chart = shallowRef(null)

function render() {
  if (!chartRef.value) return
  if (!chart.value) {
    chart.value = echarts.init(chartRef.value)
  }
  chart.value.setOption(props.option, true)
}

function handleResize() {
  chart.value?.resize()
}

onMounted(async () => {
  await nextTick()
  render()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart.value?.dispose()
  chart.value = null
})

watch(
  () => props.option,
  () => render(),
  { deep: true }
)
</script>

<style scoped>
.chart-box {
  width: 100%;
}
</style>
