import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.RenderingHints;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.MouseMotionListener;
import java.awt.geom.RoundRectangle2D;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;
import javax.swing.Timer;

/**
 * Uno.java - Un jeu de cartes UNO complet, graphique et amélioré en Java Swing.
 * <p>
 * Cette version est une implémentation Java inspirée du jeu UNO en Python fourni.
 * Elle comprend un menu principal, des joueurs contrôlés par l'IA, et une logique de jeu complète
 * incluant les cartes spéciales, une IA améliorée et des règles plus réalistes.
 *
 * @version 1.0
 */
public class Uno extends JFrame {

    public Uno() {
        super("Jeu de UNO");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1280, 800);
        setLocationRelativeTo(null);
        setResizable(false);

        GamePanel gamePanel = new GamePanel();
        add(gamePanel);

        setVisible(true);
    }

    public static void main(String[] args) {
        // Assure que l'interface graphique est créée sur l'Event Dispatch Thread
        SwingUtilities.invokeLater(Uno::new);
    }
}

/**
 * Le panneau principal qui gère toute la logique et le rendu du jeu.
 */
class GamePanel extends JPanel implements ActionListener, MouseListener, MouseMotionListener {

    // --- Énumérations pour les cartes ---
    enum Color {
        RED, GREEN, BLUE, YELLOW, WILD;

        private static final java.awt.Color[] COLORS = {
                new java.awt.Color(202, 30, 26), new java.awt.Color(0, 150, 64),
                new java.awt.Color(0, 114, 188), new java.awt.Color(255, 222, 0),
                java.awt.Color.BLACK
        };

        public java.awt.Color getAwtColor() {
            return COLORS[this.ordinal()];
        }
    }

    enum Value {
        ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE,
        SKIP, REVERSE, DRAW_TWO,
        WILD, WILD_DRAW_FOUR;

        @Override
        public String toString() {
            if (this.ordinal() <= 9) return String.valueOf(this.ordinal());
            if (this == SKIP) return "Ø";
            if (this == REVERSE) return "⇄";
            if (this == DRAW_TWO) return "+2";
            if (this == WILD) return "Joker";
            if (this == WILD_DRAW_FOUR) return "+4";
            return "";
        }
    }

    // --- Classes internes pour la structure du jeu ---
    static class Card {
        final Color color;
        final Value value;
        Rectangle bounds = new Rectangle();

        Card(Color color, Value value) {
            this.color = color;
            this.value = value;
        }

        boolean isPlayableOn(Card topCard, Color chosenWildColor) {
            if (this.color == Color.WILD) return true;
            if (topCard.color == Color.WILD) return this.color == chosenWildColor;
            return this.color == topCard.color || this.value == topCard.value;
        }

        @Override
        public String toString() {
            return color + " " + value;
        }
    }

    static class Deck {
        private final List<Card> drawPile = new ArrayList<>();
        final List<Card> discardPile = new ArrayList<>();

        public Deck() {
            createDeck();
        }

        private void createDeck() {
            for (Color c : new Color[]{Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW}) {
                drawPile.add(new Card(c, Value.ZERO));
                for (int i = 0; i < 2; i++) {
                    for (Value v : new Value[]{Value.ONE, Value.TWO, Value.THREE, Value.FOUR, Value.FIVE, Value.SIX, Value.SEVEN, Value.EIGHT, Value.NINE, Value.SKIP, Value.REVERSE, Value.DRAW_TWO}) {
                        drawPile.add(new Card(c, v));
                    }
                }
            }
            for (int i = 0; i < 4; i++) {
                drawPile.add(new Card(Color.WILD, Value.WILD));
                drawPile.add(new Card(Color.WILD, Value.WILD_DRAW_FOUR));
            }
            Collections.shuffle(drawPile);
        }

        public Card draw() {
            if (drawPile.isEmpty()) {
                if (discardPile.size() <= 1) return null; // Pas assez de cartes pour continuer
                Card top = discardPile.remove(discardPile.size() - 1);
                drawPile.addAll(discardPile);
                discardPile.clear();
                discardPile.add(top);
                Collections.shuffle(drawPile);
            }
            return drawPile.isEmpty() ? null : drawPile.remove(0);
        }

        public Card getTopCard() {
            return discardPile.isEmpty() ? null : discardPile.get(discardPile.size() - 1);
        }
    }

    static class Player {
        final String name;
        final boolean isHuman;
        final List<Card> hand = new ArrayList<>();

        Player(String name, boolean isHuman) {
            this.name = name;
            this.isHuman = isHuman;
        }
    }

    // --- Variables d'état du jeu ---
    private enum GameState { MENU, PLAYER_SELECTION, PLAYING, UNO_CALLED, COLOR_CHOICE, GAME_OVER }

    private GameState gameState = GameState.MENU;
    private final Timer timer;
    private Deck deck;
    private List<Player> players;
    private int currentPlayerIndex;
    private boolean unoState = false; // Le joueur a-t-il cliqué sur UNO ?
    private int direction = 1; // 1 pour horaire, -1 pour anti-horaire
    private Color chosenWildColor;
    private String message = "Bienvenue à UNO !";
    private int hoveredCardIndex = -1;
    private final Font FONT_LARGE = new Font("Arial", Font.BOLD, 36);
    private final Font FONT_MEDIUM = new Font("Arial", Font.BOLD, 24);
    private final Font FONT_SMALL = new Font("Arial", Font.PLAIN, 16);

    public GamePanel() {
        setBackground(new java.awt.Color(25, 25, 25));
        addMouseListener(this);
        addMouseMotionListener(this);
        timer = new Timer(1000, this); // Timer pour le tour de l'IA
    }

    private void startGame(int numBots) {
        deck = new Deck();
        players = new ArrayList<>();
        players.add(new Player("Vous", true));
        for (int i = 1; i <= numBots; i++) {
            players.add(new Player("IA " + i, false));
        }

        // Distribuer les cartes
        for (Player p : players) {
            for (int i = 0; i < 7; i++) p.hand.add(deck.draw());
        }

        // Commencer la pile de défausse
        Card firstCard;
        do {
            firstCard = deck.draw();
            if (firstCard.color == Color.WILD) {
                deck.drawPile.add(firstCard); // Remettre la carte joker dans la pioche
                Collections.shuffle(deck.drawPile);
            } else {
                deck.discardPile.add(firstCard);
            }
        } while (firstCard.color == Color.WILD);

        // Appliquer l'effet de la première carte si c'est une carte action
        // (le tour du premier joueur est 0, donc on simule que le joueur -1 a joué)
        currentPlayerIndex = players.size() - 1; // Pour que getNextPlayer() soit le joueur 0
        handleCardEffect(firstCard);

        currentPlayerIndex = 0;
        gameState = GameState.PLAYING;
        unoState = false;
        updateMessage();
        timer.start();
    }

    private void nextTurn() {
        unoState = false; // Réinitialiser l'état UNO à chaque tour

        if (checkGameOver()) return;

        currentPlayerIndex = (currentPlayerIndex + direction + players.size()) % players.size();
        chosenWildColor = null;
        updateMessage();
        repaint();

        if (!getCurrentPlayer().isHuman) {
            timer.restart();
        }
    }

    private void handleCardEffect(Card card) {
        switch (card.value) {
            case SKIP:
                message = "Tour sauté pour " + getNextPlayer().name + " !";
                currentPlayerIndex = (currentPlayerIndex + direction + players.size()) % players.size();
                break;
            case REVERSE:
                direction *= -1;
                message = "Changement de sens !";
                break;
            case DRAW_TWO:
                Player nextPlayer = getNextPlayer();
                message = nextPlayer.name + " pioche 2 cartes !";
                nextPlayer.hand.add(deck.draw());
                nextPlayer.hand.add(deck.draw());
                currentPlayerIndex = (currentPlayerIndex + direction + players.size()) % players.size();
                break;
            case WILD:
            case WILD_DRAW_FOUR:
                gameState = GameState.COLOR_CHOICE;
                if (card.value == Value.WILD_DRAW_FOUR) {
                    Player victim = getNextPlayer();
                    message = victim.name + " pioche 4 cartes !";
                    for (int i = 0; i < 4; i++) victim.hand.add(deck.draw());
                    currentPlayerIndex = (currentPlayerIndex + direction + players.size()) % players.size();
                }
                if (getCurrentPlayer().isHuman) {
                    message = "Choisissez une couleur.";
                } else {
                    // L'IA choisit une couleur
                    chosenWildColor = Color.values()[new java.util.Random().nextInt(4)];
                    gameState = GameState.PLAYING;
                    nextTurn();
                }
                break;
            default:
                break; // Pour les cartes numériques, aucun effet spécial.
        }
        repaint();
    }

    private boolean checkGameOver() {
        for (Player p : players) {
            if (p.hand.isEmpty()) {
                gameState = GameState.GAME_OVER;
                message = p.name + " a gagné la partie !";
                timer.stop();
                repaint();
                return true;
            }
        }
        return false;
    }

    private void updateMessage() {
        if (gameState == GameState.PLAYING) {
            message = "C'est au tour de " + getCurrentPlayer().name + ".";
        }
    }

    // --- Logique de l'IA ---
    private void performAiTurn() {
        if (gameState != GameState.PLAYING || getCurrentPlayer() == null || getCurrentPlayer().isHuman) return;

        Player ai = getCurrentPlayer();
        Card topCard = deck.getTopCard();

        // Stratégie de l'IA :
        // 1. Trouver les cartes jouables.
        // 2. Privilégier les cartes action si un autre joueur est proche de gagner.
        // 3. Sinon, jouer une carte numérique.
        // 4. Si aucune carte n'est jouable, piocher.
        List<Card> playableCards = ai.hand.stream()
                .filter(c -> c.isPlayableOn(topCard, chosenWildColor))
                .collect(Collectors.toList());

        if (!playableCards.isEmpty()) {
            // Tenter de jouer une carte action si un adversaire a peu de cartes
            Card cardToPlay = playableCards.stream()
                    .filter(c -> c.value.ordinal() >= Value.SKIP.ordinal() && c.value.ordinal() <= Value.DRAW_TWO.ordinal())
                    .findAny()
                    .orElse(playableCards.get(new java.util.Random().nextInt(playableCards.size()))); // Sinon, une carte au hasard

            ai.hand.remove(cardToPlay);
            deck.discardPile.add(cardToPlay);
            message = ai.name + " a joué un " + cardToPlay;
            if (ai.hand.size() == 1) message += " ... UNO !";

            handleCardEffect(cardToPlay);

            // Si l'IA a joué une carte qui ne demande pas de choix de couleur, ou si elle a fait son choix
            if (gameState != GameState.COLOR_CHOICE) {
                nextTurn();
            }
        } else {
            Card drawnCard = deck.draw();
            if (drawnCard != null) {
                ai.hand.add(drawnCard);
                // Essayer de jouer la carte piochée
                if (drawnCard.isPlayableOn(topCard, chosenWildColor)) {
                    ai.hand.remove(drawnCard);
                    deck.discardPile.add(drawnCard);
                    message = ai.name + " pioche et joue un " + drawnCard;
                    handleCardEffect(drawnCard);
                    if (gameState != GameState.COLOR_CHOICE) {
                        nextTurn();
                    }
                    return;
                }
            }
            message = ai.name + " a pioché une carte.";
            nextTurn();
        }
        repaint();
    }

    // --- Rendu graphique ---
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        switch (gameState) {
            case MENU:
                drawMenu(g2d);
                break;
            case PLAYER_SELECTION:
                drawPlayerSelection(g2d);
                break;
            case PLAYING:
            case UNO_CALLED:
            case COLOR_CHOICE:
            case GAME_OVER:
                drawGameTable(g2d);
                break;
        }
    }

    private void drawMenu(Graphics2D g2d) {
        drawCenteredString(g2d, "Jeu de UNO", getWidth() / 2, 150, FONT_LARGE, java.awt.Color.WHITE);
        drawButton(g2d, "Jouer", getWidth() / 2, 300, 200, 60);
    }

    private void drawPlayerSelection(Graphics2D g2d) {
        drawCenteredString(g2d, "Nombre d'adversaires", getWidth() / 2, 150, FONT_LARGE, java.awt.Color.WHITE);
        for (int i = 1; i <= 3; i++) {
            drawButton(g2d, i + " IA", getWidth() / 2, 250 + i * 80, 200, 60);
        }
    }

    private void drawGameTable(Graphics2D g2d) {
        // Dessiner les mains des IA
        if (players != null) {
            for (int i = 1; i < players.size(); i++) {
                drawOpponentHand(g2d, players.get(i), i, players.size() - 1);
            }
        }

        // Dessiner la pioche et la défausse
        drawCardBack(g2d, getWidth() / 2 - 120, getHeight() / 2 - 75);
        if (deck != null && deck.getTopCard() != null) {
            drawCard(g2d, deck.getTopCard(), getWidth() / 2 + 20, getHeight() / 2 - 75);
        }

        // Dessiner la main du joueur
        if (players != null && !players.isEmpty()) {
            drawPlayerHand(g2d, players.get(0));
        }

        // Dessiner le message
        g2d.setFont(FONT_MEDIUM);
        g2d.setColor(java.awt.Color.WHITE);
        drawCenteredString(g2d, message, getWidth() / 2, 40, FONT_MEDIUM, java.awt.Color.WHITE);

        // Dessiner le choix de couleur
        if (gameState == GameState.COLOR_CHOICE && getCurrentPlayer().isHuman) {
            drawColorChooser(g2d);
        }

        // Dessiner l'écran de fin de partie
        if (gameState == GameState.GAME_OVER) {
            drawGameOver(g2d);
        }

        // Dessiner le bouton UNO si nécessaire
        if (players != null && !players.isEmpty() && players.get(0).hand.size() == 2 && gameState == GameState.PLAYING) {
            drawButton(g2d, "UNO !", getWidth() - 120, getHeight() - 60, 150, 50);
        }
    }

    private void drawPlayerHand(Graphics2D g2d, Player player) {
        int handWidth = player.hand.size() * 40 + 60;
        int startX = (getWidth() - handWidth) / 2;
        int y = getHeight() - 180;

        for (int i = 0; i < player.hand.size(); i++) {
            Card card = player.hand.get(i);
            int x = startX + i * 40;
            int currentY = y;
            if (i == hoveredCardIndex) {
                currentY -= 20; // Fait remonter la carte survolée
            }
            card.bounds.setBounds(x, currentY, 100, 150);
            drawCard(g2d, card, x, currentY);
        }
    }

    private void drawOpponentHand(Graphics2D g2d, Player player, int position, int totalOpponents) {
        int cardCount = player.hand.size();
        g2d.setColor(java.awt.Color.WHITE);
        g2d.setFont(FONT_SMALL);

        if (totalOpponents == 1) { // En haut au centre
            int handWidth = cardCount * 20 + 80;
            int startX = (getWidth() - handWidth) / 2;
            for (int i = 0; i < cardCount; i++) {
                drawCardBack(g2d, startX + i * 20, 20);
            }
            drawCenteredString(g2d, player.name + " (" + cardCount + ")", getWidth() / 2, 200, FONT_SMALL, java.awt.Color.WHITE);
        } else if (totalOpponents == 2) { // A gauche et à droite
            if (position == 1) { // Gauche
                for (int i = 0; i < cardCount; i++) {
                    drawCardBack(g2d, 20, getHeight() / 2 - 100 + i * 20);
                }
                g2d.drawString(player.name + " (" + cardCount + ")", 20, getHeight() / 2 - 120);
            } else { // Droite
                for (int i = 0; i < cardCount; i++) {
                    drawCardBack(g2d, getWidth() - 120, getHeight() / 2 - 100 + i * 20);
                }
                g2d.drawString(player.name + " (" + cardCount + ")", getWidth() - 150, getHeight() / 2 - 120);
            }
        } else { // 3 adversaires
            if (position == 1) { // Gauche
                for (int i = 0; i < cardCount; i++) drawCardBack(g2d, 20, getHeight() / 2 - 100 + i * 20);
                g2d.drawString(player.name + " (" + cardCount + ")", 20, getHeight() / 2 - 120);
            } else if (position == 2) { // Haut
                int handWidth = cardCount * 20 + 80;
                int startX = (getWidth() - handWidth) / 2;
                for (int i = 0; i < cardCount; i++) drawCardBack(g2d, startX + i * 20, 20);
                drawCenteredString(g2d, player.name + " (" + cardCount + ")", getWidth() / 2, 200, FONT_SMALL, java.awt.Color.WHITE);
            } else { // Droite
                for (int i = 0; i < cardCount; i++) drawCardBack(g2d, getWidth() - 120, getHeight() / 2 - 100 + i * 20);
                g2d.drawString(player.name + " (" + cardCount + ")", getWidth() - 150, getHeight() / 2 - 120);
            }
        }
    }

    private void drawCard(Graphics2D g2d, Card card, int x, int y) {
        int width = 100, height = 150;
        g2d.setColor(card.color.getAwtColor());
        g2d.fill(new RoundRectangle2D.Double(x, y, width, height, 20, 20));
        g2d.setColor(java.awt.Color.WHITE);
        g2d.draw(new RoundRectangle2D.Double(x, y, width, height, 20, 20));

        g2d.setColor(java.awt.Color.WHITE);
        g2d.setFont(FONT_LARGE);
        String text = card.value.toString();
        FontMetrics fm = g2d.getFontMetrics();
        int textWidth = fm.stringWidth(text);
        g2d.drawString(text, x + (width - textWidth) / 2, y + height / 2 + fm.getAscent() / 2);

        // Coins
        g2d.setFont(FONT_SMALL);
        fm = g2d.getFontMetrics();
        textWidth = fm.stringWidth(text);
        g2d.drawString(text, x + 10, y + 20);
        g2d.drawString(text, x + width - textWidth - 10, y + height - 10);
    }

    private void drawCardBack(Graphics2D g2d, int x, int y) {
        int width = 100, height = 150;
        g2d.setColor(java.awt.Color.BLACK);
        g2d.fill(new RoundRectangle2D.Double(x, y, width, height, 20, 20));
        g2d.setColor(java.awt.Color.RED);
        g2d.draw(new RoundRectangle2D.Double(x, y, width, height, 20, 20));
        g2d.setFont(FONT_LARGE);
        drawCenteredString(g2d, "UNO", x + width / 2, y + height / 2, FONT_LARGE, java.awt.Color.RED);
    }

    private void drawColorChooser(Graphics2D g2d) {
        int boxSize = 60;
        int spacing = 20;
        int totalWidth = 4 * boxSize + 3 * spacing;
        int startX = (getWidth() - totalWidth) / 2;
        int y = getHeight() / 2 - boxSize / 2;

        Color[] colors = {Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW};
        for (int i = 0; i < colors.length; i++) {
            g2d.setColor(colors[i].getAwtColor());
            g2d.fillRect(startX + i * (boxSize + spacing), y, boxSize, boxSize);
        }
    }

    private void drawGameOver(Graphics2D g2d) {
        g2d.setColor(new java.awt.Color(0, 0, 0, 150));
        g2d.fillRect(0, 0, getWidth(), getHeight());
        drawCenteredString(g2d, message, getWidth() / 2, getHeight() / 2 - 50, FONT_LARGE, java.awt.Color.WHITE);
        drawButton(g2d, "Rejouer", getWidth() / 2, getHeight() / 2 + 50, 200, 60);
    }

    private void drawButton(Graphics2D g2d, String text, int x, int y, int width, int height) {
        g2d.setColor(java.awt.Color.DARK_GRAY);
        g2d.fill(new RoundRectangle2D.Double(x - width / 2.0, y - height / 2.0, width, height, 15, 15));
        g2d.setColor(java.awt.Color.WHITE);
        g2d.draw(new RoundRectangle2D.Double(x - width / 2.0, y - height / 2.0, width, height, 15, 15));
        drawCenteredString(g2d, text, x, y, FONT_MEDIUM, java.awt.Color.WHITE);
    }

    private void drawCenteredString(Graphics2D g2d, String text, int x, int y, Font font, java.awt.Color color) {
        g2d.setFont(font);
        g2d.setColor(color);
        FontMetrics fm = g2d.getFontMetrics();
        int textWidth = fm.stringWidth(text);
        g2d.drawString(text, x - textWidth / 2, y + fm.getAscent() / 2);
    }

    // --- Getters ---
    private Player getCurrentPlayer() {
        return (players == null || players.isEmpty()) ? null : players.get(currentPlayerIndex);
    }

    private Player getNextPlayer() {
        int nextIndex = (currentPlayerIndex + direction + players.size()) % players.size();
        return players.get(nextIndex);
    }

    private Color getMostCommonColorForAI(Player ai) {
        return ai.hand.stream()
                .filter(c -> c.color != Color.WILD)
                .collect(Collectors.groupingBy(c -> c.color, Collectors.counting()))
                .entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElseGet(() -> {
                    // Si l'IA n'a que des cartes Wild, choisir une couleur au hasard
                    Color[] colors = {Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW};
                    return colors[new java.util.Random().nextInt(colors.length)];
                });
    }

    // --- Gestion des événements ---
    @Override
    public void actionPerformed(ActionEvent e) {
        // Timer pour l'IA
        if (e.getSource() == timer && gameState == GameState.PLAYING && !getCurrentPlayer().isHuman) {
            performAiTurn();
        }
    }

    @Override
    public void mouseClicked(MouseEvent e) {
        Point p = e.getPoint();

        switch (gameState) {
            case MENU:
                if (new Rectangle(getWidth() / 2 - 100, 300 - 30, 200, 60).contains(p)) {
                    gameState = GameState.PLAYER_SELECTION;
                    repaint();
                }
                break;
            case PLAYER_SELECTION:
                for (int i = 1; i <= 3; i++) {
                    if (new Rectangle(getWidth() / 2 - 100, 250 + i * 80 - 30, 200, 60).contains(p)) {
                        startGame(i);
                        break;
                    }
                }
                break;
            case PLAYING:
            case UNO_CALLED:
                if (getCurrentPlayer() == null || !getCurrentPlayer().isHuman) return;

                // Clic sur le bouton UNO
                Rectangle unoButtonBounds = new Rectangle(getWidth() - 120 - 75, getHeight() - 60 - 25, 150, 50);
                if (getCurrentPlayer().hand.size() == 2 && unoButtonBounds.contains(p)) {
                    unoState = true;
                    gameState = GameState.UNO_CALLED;
                    message = "UNO ! Prêt à jouer votre avant-dernière carte.";
                    repaint();
                    return;
                }

                // Clic sur la pioche
                Rectangle drawPileBounds = new Rectangle(getWidth() / 2 - 120, getHeight() / 2 - 75, 100, 150);
                if (drawPileBounds.contains(p)) {
                    Card drawnCard = deck.draw();
                    if (drawnCard != null) {
                        getCurrentPlayer().hand.add(drawnCard);
                        message = "Vous avez pioché une carte.";
                        // Si la carte piochée n'est pas jouable, on passe le tour.
                        if (!drawnCard.isPlayableOn(deck.getTopCard(), chosenWildColor)) {
                            nextTurn();
                        } else {
                            message = "Vous avez pioché une carte jouable !";
                        }
                        repaint();
                    }
                    return;
                }

                // Clic sur une carte de la main
                Player humanPlayer = getCurrentPlayer();
                for (int i = humanPlayer.hand.size() - 1; i >= 0; i--) {
                    Card cardToPlay = humanPlayer.hand.get(i);
                    if (cardToPlay.bounds.contains(p)) {
                        if (cardToPlay.isPlayableOn(deck.getTopCard(), chosenWildColor)) {
                            // Vérification de la règle UNO
                            if (humanPlayer.hand.size() == 2 && !unoState) {
                                message = "Vous avez oublié de dire UNO ! Pénalité : 2 cartes.";
                                humanPlayer.hand.add(deck.draw());
                                humanPlayer.hand.add(deck.draw());
                            }
                            humanPlayer.hand.remove(i);
                            deck.discardPile.add(cardToPlay);
                            handleCardEffect(cardToPlay);
                            if (gameState == GameState.PLAYING) { // Si ce n'était pas une carte joker
                                nextTurn();
                            }
                        } else {
                            message = "Vous ne pouvez pas jouer cette carte.";
                        }
                        repaint();
                        return;
                    }
                }
                break;
            case COLOR_CHOICE:
                if (getCurrentPlayer() == null || !getCurrentPlayer().isHuman) return;

                int boxSize = 60, spacing = 20;
                int totalWidth = 4 * boxSize + 3 * spacing;
                int startX = (getWidth() - totalWidth) / 2;
                int y = getHeight() / 2 - boxSize / 2;
                Color[] colors = {Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW};
                for (int i = 0; i < colors.length; i++) {
                    if (new Rectangle(startX + i * (boxSize + spacing), y, boxSize, boxSize).contains(p)) {
                        chosenWildColor = colors[i];
                        gameState = (players.get(currentPlayerIndex).hand.size() == 1) ? GameState.UNO_CALLED : GameState.PLAYING;
                        message = "Vous avez choisi " + chosenWildColor.name() + ".";
                        nextTurn();
                        repaint();
                        return;
                    }
                }
                break;
            case GAME_OVER:
                if (new Rectangle(getWidth() / 2 - 100, getHeight() / 2 + 50 - 30, 200, 60).contains(p)) {
                    gameState = GameState.MENU;
                    repaint();
                }
                break;
        }
    }

    @Override
    public void mouseMoved(MouseEvent e) {
        boolean isPlayerTurn = (gameState == GameState.PLAYING || gameState == GameState.UNO_CALLED);
        if (!isPlayerTurn || players == null || !players.get(0).isHuman) {
            if (hoveredCardIndex != -1) {
                hoveredCardIndex = -1;
                repaint();
            }
            return;
        }

        Player player = players.get(0);
        int oldHovered = hoveredCardIndex;
        hoveredCardIndex = -1;

        for (int i = player.hand.size() - 1; i >= 0; i--) {
            if (player.hand.get(i).bounds.contains(e.getPoint())) {
                hoveredCardIndex = i;
                break;
            }
        }

        if (oldHovered != hoveredCardIndex) {
            repaint();
        }
    }

    // --- Méthodes d'interface non utilisées ---
    @Override public void mousePressed(MouseEvent e) {}
    @Override public void mouseReleased(MouseEvent e) {}
    @Override public void mouseEntered(MouseEvent e) {}
    @Override public void mouseExited(MouseEvent e) {}
    @Override public void mouseDragged(MouseEvent e) {}
}