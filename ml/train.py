
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay

df = pd.read_csv("ml/features.csv")
features = [c for c in df.columns if c not in ("label", "source_file", "window_index")]


is_test = df.source_file.str.contains("021")

healthy_idx = df.index[df.label == "healthy"]
cut = int(len(healthy_idx) * 0.70)
is_test.loc[healthy_idx[cut + 2:]] = True          
drop_idx = healthy_idx[cut - 2:cut + 2]           

train = df[~is_test].drop(index=drop_idx, errors="ignore")
test = df[is_test]

X_train, y_train = train[features], train["label"]
X_test, y_test = test[features], test["label"]

print(f"{len(features)} features | train {len(X_train)} | test {len(X_test)}")
print("\ntrain recordings:")
print(train.source_file.value_counts().to_string())
print("\ntest recordings:")
print(test.source_file.value_counts().to_string(), "\n")


models = {
    "Decision Tree": make_pipeline(StandardScaler(),
                                   DecisionTreeClassifier(max_depth=6, random_state=42)),
    "KNN": make_pipeline(StandardScaler(),
                         KNeighborsClassifier(n_neighbors=5)),
}

for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    print(f"{name}: accuracy {accuracy_score(y_test, pred):.3f}")
    print(classification_report(y_test, pred, digits=3))

    ConfusionMatrixDisplay.from_predictions(y_test, pred, cmap="Blues",
                                            colorbar=False, xticks_rotation=45)
    plt.title(f"{name} — held-out fault severity")
    plt.tight_layout()
    plt.savefig(f"ml/plots/confusion_{name.split()[0].lower()}.png", dpi=150)
    plt.close()


tree = models["Decision Tree"][-1]
top = pd.Series(tree.feature_importances_, index=features).nlargest(10)
top[::-1].plot.barh(figsize=(8, 4), color="#1f77b4")
plt.xlabel("Gini importance")
plt.title("Most informative features")
plt.tight_layout()
plt.savefig("ml/plots/feature_importance.png", dpi=150)
plt.close()
print("top features:\n" + top.to_string())


healthy_max = df.loc[df.label == "healthy", "rms"].quantile(0.99)
faulty_min = df.loc[df.label != "healthy", "rms"].quantile(0.01)
print(f"\nhealthy 99th pct RMS: {healthy_max:.4f}")
print(f"faulty  1st  pct RMS: {faulty_min:.4f}")
print(f"suggested boundary  : {(healthy_max + faulty_min) / 2:.4f} g")