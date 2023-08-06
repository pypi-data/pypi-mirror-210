<template>
  <div class="mb-4">
    <div v-for="item in data.items" :key="item.id">
      <ApolloMutation
        :mutation="require('./createShareMutation.graphql')"
        :variables="{ key: data.order.digitalProductsKey, orderItem: item.id }"
        @done="shareCreated"
      >
        <template #default="{ mutate, loading, error }">
          <order-item :item="item.item" read-only>
            <template #right>
              <div class="mb-2">
                {{
                  $tc("order.digital_products.licenses_bought", item.count, {
                    count: item.count,
                  })
                }}
                {{
                  $tc("order.digital_products.shares_left", item.sharesLeft, {
                    count: item.sharesLeft,
                  })
                }}
              </div>
              <div class="mb-2" v-if="item.shares.length > 0">
                <div v-for="(share, index) in item.shares" :key="share.id">
                  <v-list-item two-line>
                    <v-list-item-content>
                      <v-list-item-title
                        >{{
                          $t("order.digital_products.link_number", {
                            number: index + 1,
                          })
                        }}
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        {{
                          $t("order.digital_products.link_valid_until", {
                            date: share.shareExpiration,
                          })
                        }}
                      </v-list-item-subtitle>
                    </v-list-item-content>
                    <v-list-item-action class="flex-row">
                      <v-btn
                        icon
                        color="primary"
                        class="mr-2"
                        :href="share.shareUrl"
                        target="_blank"
                        :title="$t('order.digital_products.download')"
                      >
                        <v-icon>mdi-download</v-icon>
                      </v-btn>
                      <copy-to-clipboard-button
                        :text="share.shareUrl"
                        :title="$t('order.digital_products.copy_link')"
                      />
                    </v-list-item-action>
                  </v-list-item>
                  <v-divider v-if="index + 1 < item.shares.length" />
                </div>
              </div>
              <v-btn
                v-if="item.sharesLeft > 0"
                color="primary"
                @click="mutate"
                :disabled="loading"
                :loading="loading"
              >
                {{ $t("order.digital_products.generate_link") }}
              </v-btn>
            </template>
          </order-item>
        </template>
      </ApolloMutation>
    </div>
  </div>
</template>

<script>
import CopyToClipboardButton from "./CopyToClipboardButton.vue";
import OrderItem from "./OrderItem.vue";

export default {
  name: "DigitalProductsByOrder",
  components: { CopyToClipboardButton, OrderItem },
  methods: {
    shareCreated(data) {
      this.$emit("share-created", data);
    },
  },
  props: {
    data: {
      type: Object,
      required: true,
    },
  },
};
</script>
