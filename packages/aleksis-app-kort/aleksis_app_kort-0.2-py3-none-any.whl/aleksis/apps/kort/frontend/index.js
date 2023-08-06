export default {
  meta: {
    inMenu: true,
    titleKey: "kort.menu_title",
    icon: "mdi-card-account-details-outline",
    permission: "kort.view_menu_rule",
  },
  children: [
    {
      path: "cards/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.cards",
      meta: {
        inMenu: true,
        titleKey: "kort.card.menu_title",
        icon: "mdi-card-multiple-outline",
        permission: "kort.view_cards_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "cards/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.createCard",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "cards/:pk/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.card",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "cards/:pk/generate_pdf/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.generateCardPdf",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "cards/:pk/deactivate/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.deactivateCard",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "cards/:pk/print/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.printCard",

      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "cards/:pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.deleteCard",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "printers/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.cardPrinters",
      meta: {
        inMenu: true,
        titleKey: "kort.printer.menu_title",
        icon: "mdi-printer-outline",
        permission: "kort.view_cardprinters_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "printers/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.createCardPrinter",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "printers/:pk/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.cardPrinter",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "printers/:pk/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.editCardPrinter",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "printers/:pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.deleteCardPrinter",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "printers/:pk/config/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.cardPrinterConfig",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "layouts/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.cardLayouts",
      meta: {
        inMenu: true,
        titleKey: "kort.layout.menu_title",
        icon: "mdi-card-account-details-star-outline",
        permission: "kort.view_cardlayouts_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "layouts/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.createCardLayout",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "layouts/:pk/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.cardLayout",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "layouts/:pk/edit/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.editCardLayout",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "layouts/:pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "kort.deleteCardLayout",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
  ],
};
