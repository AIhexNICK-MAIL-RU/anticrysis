/** Объявление типов для recharts: совместимость с React 18 JSX */
import type { ComponentType } from 'react'

declare module 'recharts' {
  export const BarChart: ComponentType<any>
  export const Bar: ComponentType<any>
  export const XAxis: ComponentType<any>
  export const YAxis: ComponentType<any>
  export const CartesianGrid: ComponentType<any>
  export const Tooltip: ComponentType<any>
  export const ResponsiveContainer: ComponentType<any>
  export const PieChart: ComponentType<any>
  export const Pie: ComponentType<any>
  export const Cell: ComponentType<any>
}
