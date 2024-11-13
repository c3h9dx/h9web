import {createRouter, createWebHistory} from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'Home',
            component: DefaultLayout,
            redirect: '/dashboard',
            children: [
                {
                    path: '/dashboard',
                    name: 'Dashboard',
                    // route level code-splitting
                    // this generates a separate chunk (about.[hash].js) for this route
                    // which is lazy-loaded when the route is visited.
                    component: () => import( '@/views/Dashboard.vue' ),
                },
            ]
        },
    ],
    scrollBehavior() {
        // always scroll to top
        return { top: 0 }
    },
})

export default router
