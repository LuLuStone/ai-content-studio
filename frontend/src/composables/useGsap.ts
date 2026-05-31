import { onMounted, onUnmounted, type Ref, nextTick } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

/**
 * Stagger-in children when parent enters viewport
 */
export function useStaggerIn(
  containerRef: Ref<HTMLElement | null>,
  selector: string,
  options?: { delay?: number; stagger?: number; y?: number; duration?: number }
) {
  const { delay = 0.1, stagger = 0.06, y = 20, duration = 0.5 } = options || {}
  let ctx: gsap.Context | null = null

  onMounted(() => {
    nextTick(() => {
      if (!containerRef.value) return
      ctx = gsap.context(() => {
        gsap.fromTo(selector, { y, opacity: 0 }, {
          y: 0,
          opacity: 1,
          duration,
          stagger,
          delay,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: containerRef.value,
            start: 'top 85%',
            once: true,
          },
        })
      }, containerRef.value)
    })
  })

  onUnmounted(() => ctx?.revert())
}

/**
 * Fade-up entrance for a single element
 */
export function useFadeUp(elRef: Ref<HTMLElement | null>, options?: { delay?: number; y?: number }) {
  const { delay = 0, y = 24 } = options || {}
  let ctx: gsap.Context | null = null

  onMounted(() => {
    nextTick(() => {
      if (!elRef.value) return
      ctx = gsap.context(() => {
        gsap.fromTo(elRef.value, { y, opacity: 0 }, {
          y: 0,
          opacity: 1,
          duration: 0.6,
          delay,
          ease: 'power2.out',
        })
      }, elRef.value)
    })
  })

  onUnmounted(() => ctx?.revert())
}

/**
 * Animate a progress bar with GSAP (smoother than CSS transition)
 */
export function animateProgress(el: HTMLElement, targetWidth: number) {
  gsap.to(el, {
    width: `${targetWidth}%`,
    duration: 0.6,
    ease: 'power2.out',
  })
}

export { gsap, ScrollTrigger }
