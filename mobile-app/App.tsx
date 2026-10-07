import { useEffect, useState } from "react";
import {
  SafeAreaView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

import { getDatabase } from "./src/database/db";
import { useConnectivity } from "./src/hooks/useConnectivity";
import {
  addToSyncQueue,
  getPendingSyncCount,
} from "./src/services/syncQueue";

export default function App() {
  const isOnline = useConnectivity();

  const [pendingCount, setPendingCount] =
      useState(0);

  async function refreshQueueCount() {
    const count = await getPendingSyncCount();
    setPendingCount(count);
  }

  useEffect(() => {
    async function initialiseApp() {
      await getDatabase();
      await refreshQueueCount();
    }

    initialiseApp();
  }, []);

  async function simulateOfflineAction() {
    await addToSyncQueue(
        "POST",
        "/api/patient/profile",
        {
          example: "offline test action",
        }
    );

    await refreshQueueCount();
  }

  return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.title}>
          Umdeni Health Lite
        </Text>

        <Text style={styles.subtitle}>
          Your health records, even when connectivity
          is limited.
        </Text>

        <View style={styles.card}>
          <Text style={styles.label}>
            Connection
          </Text>

          <Text style={styles.value}>
            {isOnline === null
                ? "Checking..."
                : isOnline
                    ? "Online"
                    : "Offline"}
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>
            Waiting to sync
          </Text>

          <Text style={styles.queueNumber}>
            {pendingCount}
          </Text>

          <Text style={styles.description}>
            Actions created offline stay safely on
            this device until connectivity returns.
          </Text>
        </View>

        <TouchableOpacity
            style={styles.button}
            onPress={simulateOfflineAction}
        >
          <Text style={styles.buttonText}>
            Add Offline Test Action
          </Text>
        </TouchableOpacity>
      </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    justifyContent: "center",
  },

  title: {
    fontSize: 30,
    fontWeight: "700",
    marginBottom: 8,
  },

  subtitle: {
    fontSize: 16,
    marginBottom: 32,
  },

  card: {
    padding: 20,
    borderWidth: 1,
    borderRadius: 16,
    marginBottom: 16,
  },

  label: {
    fontSize: 14,
    marginBottom: 8,
  },

  value: {
    fontSize: 22,
    fontWeight: "600",
  },

  queueNumber: {
    fontSize: 36,
    fontWeight: "700",
    marginVertical: 6,
  },

  description: {
    fontSize: 14,
    lineHeight: 20,
  },

  button: {
    padding: 16,
    borderRadius: 14,
    alignItems: "center",
    borderWidth: 1,
    marginTop: 8,
  },

  buttonText: {
    fontSize: 16,
    fontWeight: "600",
  },
});