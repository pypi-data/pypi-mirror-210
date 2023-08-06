export default {
  meta: {
    inMenu: true,
    titleKey: "fritak.menu_title",
    icon: "mdi-clipboard-account-outline",
    permission: "fritak.view_menu_rule",
  },
  props: {
    byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
  },
  children: [
    {
      path: "",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "fritak.fritakIndex",
      meta: {
        inMenu: true,
        titleKey: "fritak.my_requests.menu_title",
        icon: "mdi-account-details-outline",
        permission: "fritak.view_index_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "apply_for/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "fritak.fritakApplyFor",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "details/:id_/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "fritak.fritakDetails",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "edit/:id_/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "fritak.fritakEdit",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "applied_for/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "fritak.fritakAppliedFor",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "check1/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "fritak.fritakCheck1",
      meta: {
        inMenu: true,
        titleKey: "fritak.check.menu_title_1",
        icon: "mdi-check",
        permission: "fritak.check1_exemptionrequest_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "check2/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "fritak.fritakCheck2",
      meta: {
        inMenu: true,
        titleKey: "fritak.check.menu_title_2",
        icon: "mdi-check-all",
        permission: "fritak.check2_exemptionrequest_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "archive/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "fritak.fritakArchive",
      meta: {
        inMenu: true,
        titleKey: "fritak.archive.menu_title",
        icon: "mdi-archive-outline",
        permission: "fritak.view_archive_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "archive/print/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "fritak.fritakPrintArchive",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
  ],
};
