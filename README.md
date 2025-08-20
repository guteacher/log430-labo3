# Labo 03 – REST APIs, GraphQL

<img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Ets_quebec_logo.png" width="250">    
ÉTS - LOG430 - Architecture logicielle - Chargé de laboratoire: Gabriel C. Ullmann, Automne 2025.

## 🎯 Objectifs d'apprentissage

- Comprendre ce qu'est une API REST.
- Comprendre comment une API peut contribuer à l'extensibilité d'une application et faciliter l'intégration de nouveaux clients.
- Apprendre comment utiliser GraphQL pour créer une API plus flexible offrant aux clients la possibilité de requêter exactement les données dont ils ont besoin.
- Comparer les avantages et inconvénients des approches REST et GraphQL selon différents contextes d'utilisation.
- Maîtriser la gestion d'état et de cache avec Redis dans un contexte d'API moderne.

## ⚙️ Setup

Dans ce laboratoire, nous poursuivrons le développement de notre application de gestion de magasin. Nous ajoutons maintenant la gestion du stock des articles, en complément de la gestion des commandes, des articles et des utilisateurs.

- Chaque fois qu’une commande est passée, le stock des articles concernés est diminué.
- Si une commande est supprimée, les articles correspondants sont réintégrés dans le stock.

> 📝 NOTE : à ce stade, nous ne mettons pas en place de gestion du statut des commandes, des limites minimums/maximums de stock ni de mécanisme d’authentification pour l’API. L’objectif est de nous concentrer sur les aspects architecturaux, et non sur les aspects métier ou de sécurité. La logique de l’application sera donc volontairement simplifiée.

Nous ajouterons également une nouvelle route permettant à nos fournisseurs de consulter l’état de notre stock et nous envoyer de nouveaux articles pour le réapprovisionner. Pour cette route en particulier, nous autoriserons l’utilisation de GraphQL, afin que le client puisse choisir précisément les colonnes qu’il souhaite checher dans la base de données. Cela permet de résoudre un problème classique des API REST : renvoyer trop ou pas assez de données.

### 1. Faites un fork et clonez le dépôt GitLab

```bash
git clone https://github.com/guteacher/log430-a25-labo3
cd log430-a25-labo3
```

### 2. Préparez l'environnement de développement

Suivez les mêmes étapes que dans le laboratoire 00.

### 3. Installez Postman

Installez Postman et importez la collection disponible dans /docs/collections.

### 4. Comprendre les principes REST

À ce stade, notre application est une API qui respecte presque tous les principes REST définis par Roy Fielding dans sa thèse de doctorat (2000) :

- ✅ Client–Serveur : séparation claire entre client et serveur.
- ✅ Système en couches : notre application comporte trois couches (front-end, back-end, base de données).
- ✅ Sans état (stateless) : chaque requête est indépendante, le serveur ne « se souvient » pas des requêtes précédentes.
- ⛔ Cache : il n’y a pas de mécanisme de cache côté client (nous utilisons Postman, mais cela serait possible avec un vrai front-end).
- ✅ Interface uniforme : les endpoints sont bien nommés et utilisent les bonnes méthodes HTTP (POST /orders, GET /products/:id, etc.).

Une API qui respecte l’ensemble de ces principes est appelée une API RESTful. Pour l’instant, nous travaillons uniquement avec une API REST.

## 🧪 Activités pratiques

### 1. Permettre l'accès à l'API

Ouvrez les ports nécessaires dans le fichier docker-compose.yml afin de permettre l'accès à l'API (port 5000) :

```yaml
store_manager:
  build: .
  volumes:
    - .:/app
  ports:
    - "5000:5000" # REST API
```

### 2. Faire l'ajout de stock
Initiallement, nous avons besoin de setter les stock levels pour nos articles dans la base de donnés. Dans le ficihier `src/commands/write_product_stock.py`, completez les lignes manquantes à `set_stock_for_product` pour nous permettre de faire ça.

### 3. Test : vérifier l'ajout de stock

Testez votre implémentation en utilisant la route `POST /product_stocks/<int:product_id>` via Postman. 

> 💡 **Question 1** : Quelles sont les étapes pour tester cette fonctionnalité ? Décrivez le processus complet : quelle route Postman appeler en premier, comment vérifier que les données sont bien ajoutées dans Redis, et quelle autre route utiliser pour valider le résultat.

### 4. Faire la mise à jour de stock à Redis

Dans le fichier `src/commands/write_order.py`, dans la méthode `insert_order`, implémentez la fonctionnalité de mise à jour de stock dans Redis. La mise à jour de stock dans MySQL ce dèjá faite. De toute façon, assurez-vous de maintenir la cohérence entre les opérations MySQL et Redis en faisant les operation Redis après le commit des operation MySQL.

```python
    # Pseudo code
    do_logic_to_add_order()
    do_logic_to_add_order_items(order_items)
    check_out_items_from_stock(session, order_items)
    session.commit()
    update_stock_redis(order_items, '-')
```

> 💡 **Question 2** : Quelles méthodes avez-vous utilisées pour ajouter des données de stock dans MySQL et Redis ? Veuillez inclure le code pour illustrer votre réponse.

### 5. Mettre à jour le stock dans Redis (delete/update)

Dans le fichier `src/commands/write_order.py`, dans la méthode `delete_order`, implémentez la mise à jour du stock dans Redis lors de suppressions. Ici, la logique c'est l'invers a l`exercise anterieur : en lieu de diminuer la quantite de larticle dans le stock, nousv voulons faire la quantite monter pour restorer le stock. De la meme façon, assurez-vous de maintenir la cohérence entre les opérations MySQL et Redis en faisant les operation Redis après le commit des operation MySQL.

> 💡 **Question 3** : Selon vous, dans un application de gestion de commande reel, esc-ce que on pourrait restorer le stock toujours? Écrivez un pseudo code en montrant les verifications que nous devrions fair avant de restorer le stock.

### 5. Créer une route GraphQL pour les fournisseurs
TODO: write new description

### 6. Test : requête GraphQL pour fournisseurs
TODO: mention route
Testez votre implémentation GraphQL en utilisant l'interface Postman.

### 7. Ajouter plus d'informations aux articles dans Redis

Enrichissez les données des articles stockées dans Redis en ajoutant des informations comme la description, le prix, la catégorie, etc.

> 💡 **Question 4** : Quelles commandes avez-vous utilisées pour ajouter un dictionnaire dans Redis ? Veuillez inclure le code pour illustrer votre réponse.

### 8. Utiliser GraphQL pour sélectionner des informations flexibles
TODO: write new description

> 💡 **Question 5** : Serait-il préférable de créer plusieurs routes REST avec différentes combinaisons d'attributs, ou d'utiliser une seule route GraphQL flexible ? Analysez les avantages et inconvénients de chaque approche en termes de maintenance, performance et expérience développeur.

## 📦 Livrables

- Un fichier .zip contenant l'intégralité du code source du projet Labo 03.
- Un rapport en .pdf répondant aux 5 questions présentées dans ce document. Il est obligatoire d'illustrer vos réponses avec du code ou des captures d'écran/terminal.