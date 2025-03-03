import {createRouter, createWebHashHistory, createWebHistory} from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout'
import {h, resolveComponent} from "vue";
import dashboard from "@/views/dashboard.vue";

const router = createRouter({
    // history: createWebHistory(import.meta.env.BASE_URL),
    history: createWebHashHistory(import.meta.env.BASE_URL),
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
                    component: dashboard,
                    meta: { requiresAuth: true },
                },
                {
                    path: '/nodes',
                    name: 'Nodes',
                    component: () => import( '@/views/nodes.vue' ),
                    meta: { requiresAuth: true },
                },
                {
                    path: '/rawframe',
                    name: 'Raw frame',
                    component: () => import( '@/views/rawframe.vue' ),
                    meta: { requiresAuth: true },
                },
                {
                    path: '/stats',
                    name: 'Stats',
                    component: () => import( '@/views/stats.vue' ),
                    meta: { requiresAuth: true },
                },
                {
                    path: '/settings',
                    name: 'Settings',
                    component: () => import( '@/views/settings.vue' ),
                    meta: { requiresAuth: true },
                },
            ]
        },
        {
          path: '/',
          redirect: '/404',
          name: 'Pages',
          component: {
            render() {
              return h(resolveComponent('router-view'))
            },
          },
          children: [
            {
              path: '404',
              name: 'Page404',
              component: () => import('@/views/Page404'),
            },
            {
              path: '500',
              name: 'Page500',
              component: () => import('@/views/Page500'),
            },
            {
              path: 'login',
              name: 'Login',
              component: () => import('@/views/Login'),
            },
          ],
        },
        {
            path: "/:pathMatch(.*)*",
            component: () => import('@/views/Page404')
        }
    ],
    scrollBehavior() {
        // always scroll to top
        return { top: 0 }
    },
})

function getCookie(cname) {
    let name = cname + "=";
    let ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

router.beforeEach((to, from, next) => {
    if (to.matched.some((record) => record.meta.requiresAuth)) {
        if (getCookie("authenticated")) {
            next();
            return;
        }
        next("/login");
    } else {
        next();
    }
});

export default router
