import java.awt.BorderLayout;
import java.awt.CardLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.Point;
import java.awt.RenderingHints;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.List;

import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.SwingUtilities;
import javax.swing.SwingWorker;
import javax.swing.Timer;
import javax.swing.border.EmptyBorder;

/**
 * Chess.java - Un jeu d'échecs complet, graphique et avec IA.
 * <p>
 * Ce fichier unique contient toute la logique pour un jeu d'échecs.
 * Il inclut :
 * - Un menu pour choisir entre Humain vs Humain ou Humain vs IA.
 * - Une IA propulsée par le moteur Stockfish avec plusieurs niveaux de difficulté.
 * - Une interface graphique améliorée avec un historique des coups.
 * - La gestion complète des règles : roque, prise en passant, promotion du pion (avec choix).
 * - La détection d'échec, d'échec et mat, et de pat.
 *
 * @version 3.0
 */
public class Chess extends JFrame {

    public Chess() {
        super("Jeu d'Échecs");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setResizable(false);
        
        // Le CardLayout permet de basculer entre le menu et le jeu
        CardLayout cardLayout = new CardLayout();
        JPanel mainPanel = new JPanel(cardLayout);

        MenuPanel menuPanel = new MenuPanel(mainPanel, cardLayout);
        mainPanel.add(menuPanel, "menu");
        
        add(mainPanel);
        cardLayout.show(mainPanel, "menu");

        pack();
        setLocationRelativeTo(null);

        // S'assurer que le moteur Stockfish s'arrête à la fermeture
        addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosing(WindowEvent e) {
                menuPanel.closeEngine();
            }
        });
        setVisible(true);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(Chess::new);
    }
}

/**
 * Panneau du menu principal pour choisir le mode de jeu.
 */
class MenuPanel extends JPanel {
    private StockfishClient stockfishClient;

    public MenuPanel(JPanel mainPanel, CardLayout cardLayout) {
        setPreferredSize(new Dimension(840, 690));
        setBackground(new Color(40, 40, 40));
        setLayout(new GridBagLayout());

        JLabel title = new JLabel("Jeu d'Échecs");
        title.setFont(new Font("Serif", Font.BOLD, 60));
        title.setForeground(Color.WHITE);

        JButton pvpButton = new JButton("Humain vs Humain");
        JButton easyButton = new JButton("IA Facile");
        JButton mediumButton = new JButton("IA Moyenne");
        JButton hardButton = new JButton("IA Difficile");

        Font buttonFont = new Font("Arial", Font.BOLD, 24);
        pvpButton.setFont(buttonFont);
        easyButton.setFont(buttonFont);
        mediumButton.setFont(buttonFont);
        hardButton.setFont(buttonFont);

        pvpButton.addActionListener(e -> {
            startGame(mainPanel, cardLayout, false, 0);
        });

        easyButton.addActionListener(e -> startGame(mainPanel, cardLayout, true, 1));
        mediumButton.addActionListener(e -> startGame(mainPanel, cardLayout, true, 10));
        hardButton.addActionListener(e -> startGame(mainPanel, cardLayout, true, 20));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridwidth = GridBagConstraints.REMAINDER;
        gbc.insets = new Insets(20, 0, 50, 0);
        add(title, gbc);

        gbc.insets = new Insets(10, 0, 10, 0);
        gbc.ipadx = 50;
        gbc.ipady = 20;
        add(pvpButton, gbc);
        add(easyButton, gbc);
        add(mediumButton, gbc);
        add(hardButton, gbc);
    }

    private void startGame(JPanel mainPanel, CardLayout cardLayout, boolean vsAI, int skillLevel) {
        try {
            stockfishClient = vsAI ? new StockfishClient() : null;
            ChessGamePanel gamePanel = new ChessGamePanel(mainPanel, cardLayout, vsAI, skillLevel, stockfishClient);
            mainPanel.add(gamePanel, "game");
            cardLayout.show(mainPanel, "game");
        } catch (IOException ex) {
            JOptionPane.showMessageDialog(this, "Erreur: Le moteur Stockfish n'a pas pu être démarré.\n" +
                    "Veuillez vous assurer que 'stockfish.exe' se trouve dans le même dossier que le jeu.", "Erreur Moteur", JOptionPane.ERROR_MESSAGE);
        }
    }

    public void closeEngine() {
        if (stockfishClient != null) {
            stockfishClient.close();
        }
    }
}

/**
 * Panneau principal contenant le plateau de jeu et les informations annexes.
 */
class ChessGamePanel extends JPanel {
    public ChessGamePanel(JPanel mainPanel, CardLayout cardLayout, boolean vsAI, int skillLevel, StockfishClient client) {
        setLayout(new BorderLayout());

        ChessPanel chessPanel = new ChessPanel(vsAI, skillLevel, client);
        add(chessPanel, BorderLayout.CENTER);

        JPanel sidePanel = new JPanel();
        sidePanel.setLayout(new BoxLayout(sidePanel, BoxLayout.Y_AXIS));
        sidePanel.setPreferredSize(new Dimension(200, 690));
        sidePanel.setBackground(new Color(240, 240, 240));
        sidePanel.setBorder(new EmptyBorder(10, 10, 10, 10));

        JButton newGameButton = new JButton("Nouvelle Partie");
        newGameButton.addActionListener(e -> {
            if (client != null) {
                client.sendUciNewGame();
            }
            cardLayout.show(mainPanel, "menu");
            mainPanel.remove(this);
        });

        JTextArea moveHistory = new JTextArea();
        moveHistory.setEditable(false);
        chessPanel.setMoveHistory(moveHistory);
        JScrollPane scrollPane = new JScrollPane(moveHistory);

        sidePanel.add(newGameButton);
        sidePanel.add(Box.createRigidArea(new Dimension(0, 10)));
        sidePanel.add(new JLabel("Historique des coups:"));
        sidePanel.add(scrollPane);

        add(sidePanel, BorderLayout.EAST);
    }
}

/**
 * Le panneau principal qui gère le plateau, la logique et les interactions du jeu.
 */
class ChessPanel extends JPanel {

    private static final int BOARD_SIZE = 8;
    private static final int SQUARE_SIZE = 80;
    private Piece[][] board = new Piece[BOARD_SIZE][BOARD_SIZE];
    private Piece selectedPiece;
    private List<Point> validMoves = new ArrayList<>();
    private boolean isWhiteTurn = true;
    private String statusMessage = "Au tour des Blancs de jouer.";
    private boolean gameOver = false;
    private final boolean vsAI;
    private final int skillLevel;
    private final StockfishClient stockfishClient;
    private JTextArea moveHistory;
    private int moveCount = 1;
    private final List<String> moveHistoryAlgebraic = new ArrayList<>();

    public ChessPanel(boolean vsAI, int skillLevel, StockfishClient client) {
        setPreferredSize(new Dimension(BOARD_SIZE * SQUARE_SIZE, BOARD_SIZE * SQUARE_SIZE + 50));
        setBackground(Color.DARK_GRAY);
        this.vsAI = vsAI;
        this.skillLevel = skillLevel;
        this.stockfishClient = client;
        setupBoard();

        addMouseListener(new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent e) {
                handleMouseClick(e.getX(), e.getY());
            }
        });
    }

    public void setMoveHistory(JTextArea moveHistory) {
        this.moveHistory = moveHistory;
    }

    private void handleMouseClick(int x, int y) {
        if (gameOver || (vsAI && !isWhiteTurn) || y >= BOARD_SIZE * SQUARE_SIZE) return;

        int col = x / SQUARE_SIZE; // Note: x is for columns
        int row = y / SQUARE_SIZE;

        if (selectedPiece == null) {
            // Sélectionner une pièce
            Piece piece = board[row][col];
            if (piece != null && piece.isWhite == isWhiteTurn) {
                selectedPiece = piece;
                validMoves = piece.getLegalMoves(board);
            }
        } else {
            // Déplacer la pièce sélectionnée
            boolean isValidMove = false;
            for (Point move : validMoves) {
                if (move.x == row && move.y == col) {
                    isValidMove = true;
                    break;
                }
            }

            if (isValidMove) {
                movePiece(selectedPiece, row, col);
            } else {
                // Si on clique sur une autre de nos pièces, on la sélectionne
                Piece clickedPiece = board[row][col];
                if (clickedPiece != null && clickedPiece.isWhite == isWhiteTurn) {
                    selectedPiece = clickedPiece;
                    validMoves = clickedPiece.getLegalMoves(board);
                } else {
                    selectedPiece = null;
                    validMoves.clear();
                }
            }
        }
        repaint();
    }

    private void performAiMove() {
        statusMessage = "L'IA réfléchit...";
        repaint();

        SwingWorker<String, Void> worker = new SwingWorker<>() {
            @Override
            protected String doInBackground() throws Exception {
                return stockfishClient.getBestMove(moveHistoryAlgebraic, skillLevel);
            }

            @Override
            protected void done() {
                try {
                    String bestMove = get();
                    if (bestMove != null) {
                        Point from = parseAlgebraic(bestMove.substring(0, 2));
                        Point to = parseAlgebraic(bestMove.substring(2, 4));
                        Piece pieceToMove = board[from.x][from.y];
                        movePiece(pieceToMove, to.x, to.y);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    statusMessage = "Erreur de l'IA.";
                }
                repaint();
            }
        };
        worker.execute();
    }

    private void movePiece(Piece piece, int newRow, int newCol) {
        int oldRow = piece.row;
        int oldCol = piece.col;
        Piece capturedPiece = board[newRow][newCol];

        // Gestion de la prise "en passant"
        if (piece instanceof Pawn && newCol != oldCol && capturedPiece == null) {
            board[oldRow][newCol] = null;
        }

        // Gestion du roque
        if (piece instanceof King && Math.abs(newCol - oldCol) == 2) {
            if (newCol > oldCol) { // Petit roque
                Piece rook = board[oldRow][7];
                board[oldRow][5] = rook;
                board[oldRow][7] = null;
                rook.col = 5;
            } else { // Grand roque
                Piece rook = board[oldRow][0];
                board[oldRow][3] = rook;
                board[oldRow][0] = null;
                rook.col = 3;
            }
        }

        board[newRow][newCol] = piece;
        board[oldRow][oldCol] = null;
        piece.row = newRow;
        piece.col = newCol; // This was missing in the original logic for rooked rooks
        piece.hasMoved = true;

        // Log move for display and for the engine
        String algebraicMove = toAlgebraic(oldRow, oldCol) + toAlgebraic(newRow, newCol);
        String displayMove = getDisplayMoveString(piece, toAlgebraic(oldRow, oldCol), algebraicMove.substring(2), capturedPiece != null);
        if (isWhiteTurn) {
            moveHistory.append(moveCount + ". " + displayMove);
        } else {
            moveHistory.append("  " + displayMove + "\n");
            moveCount++;
        }

        // Promotion du pion
        if (piece instanceof Pawn && (newRow == 0 || newRow == 7)) {
            Object[] options = {"Dame", "Tour", "Fou", "Cavalier"};
            int choice = JOptionPane.showOptionDialog(this, "Choisissez la pièce pour la promotion :",
                    "Promotion du Pion", JOptionPane.DEFAULT_OPTION, JOptionPane.PLAIN_MESSAGE,
                    null, options, options[0]);

            if (choice == 0) board[newRow][newCol] = new Queen(piece.isWhite, newRow, newCol);
            else if (choice == 1) board[newRow][newCol] = new Rook(piece.isWhite, newRow, newCol);
            else if (choice == 2) board[newRow][newCol] = new Bishop(piece.isWhite, newRow, newCol);
            else if (choice == 3) board[newRow][newCol] = new Knight(piece.isWhite, newRow, newCol);
            else board[newRow][newCol] = new Queen(piece.isWhite, newRow, newCol); // Default to Queen
            algebraicMove += "q"; // Append promotion char, assuming queen for simplicity for engine
        }
        moveHistoryAlgebraic.add(algebraicMove);

        // Réinitialiser l'état "en passant" pour tous les pions
        for (int r = 0; r < BOARD_SIZE; r++) {
            for (int c = 0; c < BOARD_SIZE; c++) {
                if (board[r][c] instanceof Pawn) {
                    ((Pawn) board[r][c]).enPassantVulnerable = false;
                }
            }
        }
        // Marquer le pion qui vient de bouger de 2 cases
        if (piece instanceof Pawn && Math.abs(newRow - oldRow) == 2) {
            ((Pawn) piece).enPassantVulnerable = true;
        }

        isWhiteTurn = !isWhiteTurn;
        selectedPiece = null;
        validMoves.clear();
        updateStatus();

        if (!gameOver && vsAI && !isWhiteTurn) { // It's AI's turn
            // Use a timer to make the AI move feel less instant
            Timer timer = new Timer(100, e -> performAiMove());
            timer.setRepeats(false);
            timer.start();
        }
    }

    private void updateStatus() {
        boolean inCheck = isKingInCheck(isWhiteTurn, board);
        boolean hasLegalMoves = false;
        for (int r = 0; r < BOARD_SIZE; r++) {
            for (int c = 0; c < BOARD_SIZE; c++) {
                Piece p = board[r][c];
                if (p != null && p.isWhite == isWhiteTurn) {
                    if (!p.getLegalMoves(board).isEmpty()) {
                        hasLegalMoves = true;
                        break;
                    }
                }
            }
            if (hasLegalMoves) break;
        }

        if (!hasLegalMoves) {
            if (inCheck) {
                statusMessage = "Échec et mat ! " + (isWhiteTurn ? "Les Noirs" : "Les Blancs") + " ont gagné.";
                moveHistory.append("\n" + statusMessage);
                gameOver = true;
            } else {
                statusMessage = "Pat ! Match nul.";
                moveHistory.append("\n" + statusMessage);
                gameOver = true;
            }
        } else {
            statusMessage = "Au tour des " + (isWhiteTurn ? "Blancs" : "Noirs") + " de jouer." + (inCheck ? " (Échec)" : "");
        }
        repaint();
    }

    private String getDisplayMoveString(Piece piece, String from, String to, boolean isCapture) {
        String pieceSymbol = "";
        // Pawn moves don't use a symbol unless it's a capture
        if (piece instanceof Pawn) {
            if (isCapture) pieceSymbol = from.substring(0, 1);
        } else if (piece instanceof Knight) pieceSymbol = "N";
        else if (piece instanceof Bishop) pieceSymbol = "B";
        else if (piece instanceof Rook) pieceSymbol = "R";
        else if (piece instanceof Queen) pieceSymbol = "Q";
        else if (piece instanceof King) pieceSymbol = "K";

        return pieceSymbol + (isCapture ? "x" : "") + to;
    }

    private String toAlgebraic(int row, int col) {
        return "" + (char)('a' + col) + (8 - row);
    }

    private Point parseAlgebraic(String alg) {
        int col = alg.charAt(0) - 'a';
        int row = 8 - (alg.charAt(1) - '0');
        return new Point(row, col);
    }

    public static boolean isKingInCheck(boolean isWhiteKing, Piece[][] boardState) {
        Point kingPos = null;
        for (int r = 0; r < BOARD_SIZE; r++) {
            for (int c = 0; c < BOARD_SIZE; c++) {
                Piece p = boardState[r][c];
                if (p instanceof King && p.isWhite == isWhiteKing) {
                    kingPos = new Point(p.row, p.col);
                    break;
                }
            }
            if (kingPos != null) break;
        }
        if (kingPos == null) return false; // Ne devrait jamais arriver

        for (int r = 0; r < BOARD_SIZE; r++) {
            for (int c = 0; c < BOARD_SIZE; c++) {
                Piece p = boardState[r][c];
                // A king cannot directly attack another king, so we can skip checking the opponent's king moves.
                // This also prevents the infinite recursion that could cause a StackOverflowError.
                if (p != null && p.isWhite != isWhiteKing && !(p instanceof King)) {
                    for (Point move : p.getPseudoLegalMoves(boardState)) {
                        if (move.x == kingPos.x && move.y == kingPos.y) {
                            return true;
                        }
                    }
                }
            }
        }
        return false;
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Dessiner le plateau
        for (int row = 0; row < BOARD_SIZE; row++) {
            for (int col = 0; col < BOARD_SIZE; col++) {
                Color squareColor = ((row + col) % 2 == 0) ? new Color(238, 238, 210) : new Color(118, 150, 86);
                g.setColor(squareColor);
                g.fillRect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE);
            }
        }

        // Mettre en surbrillance la case sélectionnée
        if (selectedPiece != null) {
            g.setColor(new Color(255, 255, 0, 100));
            g.fillRect(selectedPiece.col * SQUARE_SIZE, selectedPiece.row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE);
        }

        // Dessiner les mouvements valides
        g.setColor(new Color(0, 0, 0, 80));
        for (Point move : validMoves) {
            g.fillOval(move.y * SQUARE_SIZE + SQUARE_SIZE / 3, move.x * SQUARE_SIZE + SQUARE_SIZE / 3, SQUARE_SIZE / 3, SQUARE_SIZE / 3);
        }

        // Dessiner les pièces
        g2d.setFont(new Font("Serif", Font.PLAIN, 60));
        for (int row = 0; row < BOARD_SIZE; row++) {
            for (int col = 0; col < BOARD_SIZE; col++) {
                Piece piece = board[row][col];
                if (piece != null) {
                    g2d.setColor(piece.isWhite ? Color.WHITE : Color.BLACK);
                    FontMetrics fm = g2d.getFontMetrics();
                    int stringWidth = fm.stringWidth(piece.getSymbol());
                    int stringHeight = fm.getAscent();
                    g2d.drawString(piece.getSymbol(), col * SQUARE_SIZE + (SQUARE_SIZE - stringWidth) / 2, row * SQUARE_SIZE + (SQUARE_SIZE + stringHeight) / 2 - 5);
                }
            }
        }

        // Dessiner la zone de statut
        g.setColor(Color.WHITE);
        g.fillRect(0, BOARD_SIZE * SQUARE_SIZE, getWidth(), 50);
        g.setColor(Color.BLACK);
        g.setFont(new Font("Arial", Font.BOLD, 20));
        FontMetrics fm = g.getFontMetrics();
        int stringWidth = fm.stringWidth(statusMessage); // This can be pre-calculated
        g.drawString(statusMessage, (getWidth() - stringWidth) / 2, BOARD_SIZE * SQUARE_SIZE + 32);
    }

    private void setupBoard() {
        // Pions
        for (int i = 0; i < 8; i++) {
            board[1][i] = new Pawn(false, 1, i);
            board[6][i] = new Pawn(true, 6, i);
        }
        // Tours
        board[0][0] = new Rook(false, 0, 0);
        board[0][7] = new Rook(false, 0, 7);
        board[7][0] = new Rook(true, 7, 0);
        board[7][7] = new Rook(true, 7, 7);
        // Cavaliers
        board[0][1] = new Knight(false, 0, 1);
        board[0][6] = new Knight(false, 0, 6);
        board[7][1] = new Knight(true, 7, 1);
        board[7][6] = new Knight(true, 7, 6);
        // Fous
        board[0][2] = new Bishop(false, 0, 2);
        board[0][5] = new Bishop(false, 0, 5);
        board[7][2] = new Bishop(true, 7, 2);
        board[7][5] = new Bishop(true, 7, 5);
        // Dames
        board[0][3] = new Queen(false, 0, 3);
        board[7][3] = new Queen(true, 7, 3);
        // Rois
        board[0][4] = new King(false, 0, 4);
        board[7][4] = new King(true, 7, 4);

        // Reset state
        isWhiteTurn = true;
        gameOver = false;
        statusMessage = "Au tour des Blancs de jouer.";
        moveHistoryAlgebraic.clear();
        moveCount = 1;
    }
}

abstract class Piece {
    boolean isWhite;
    int row, col;
    boolean hasMoved = false;

    public Piece(boolean isWhite, int row, int col) {
        this.isWhite = isWhite;
        this.row = row;
        this.col = col;
    }

    abstract String getSymbol();

    abstract List<Point> getPseudoLegalMoves(Piece[][] board);

    public List<Point> getLegalMoves(Piece[][] board) {
        List<Point> legalMoves = new ArrayList<>();
        for (Point move : getPseudoLegalMoves(board)) {
            // Sauvegarde l'état avant de simuler le coup
            int oldRow = this.row;
            int oldCol = this.col;
            int newRow = move.x;
            int newCol = move.y;
            Piece targetPiece = board[newRow][newCol];

            // Simule le coup
            board[newRow][newCol] = this;
            board[oldRow][oldCol] = null;
            this.row = newRow;
            this.col = newCol;

            // Vérifie si le roi est en échec après le coup
            if (!ChessPanel.isKingInCheck(this.isWhite, board)) {
                legalMoves.add(move);
            }

            // Annule le coup pour restaurer l'échiquier
            board[oldRow][oldCol] = this;
            board[newRow][newCol] = targetPiece;
            this.row = oldRow;
            this.col = oldCol;
        }
        return legalMoves;
    }

    protected boolean isValid(int r, int c) {
        return r >= 0 && r < 8 && c >= 0 && c < 8;
    }

    protected void addLineMoves(List<Point> moves, Piece[][] board, int[] dRow, int[] dCol) {
        for (int i = 0; i < dRow.length; i++) {
            for (int j = 1; j < 8; j++) {
                int newRow = row + j * dRow[i];
                int newCol = col + j * dCol[i];
                if (!isValid(newRow, newCol)) break;
                Piece target = board[newRow][newCol];
                if (target == null) {
                    moves.add(new Point(newRow, newCol));
                } else {
                    if (target.isWhite != this.isWhite) {
                        moves.add(new Point(newRow, newCol));
                    }
                    break;
                }
            }
        }
    }
}

class King extends Piece {
    public King(boolean isWhite, int row, int col) {
        super(isWhite, row, col);
    }

    @Override
    String getSymbol() {
        return isWhite ? "♔" : "♚";
    }

    @Override
    List<Point> getPseudoLegalMoves(Piece[][] board) {
        List<Point> moves = new ArrayList<>();
        int[] dRow = {-1, -1, -1, 0, 0, 1, 1, 1};
        int[] dCol = {-1, 0, 1, -1, 1, -1, 0, 1};

        for (int i = 0; i < 8; i++) {
            int newRow = row + dRow[i];
            int newCol = col + dCol[i];
            if (isValid(newRow, newCol)) {
                Piece target = board[newRow][newCol];
                if (target == null || target.isWhite != this.isWhite) {
                    moves.add(new Point(newRow, newCol));
                }
            }
        }

        // Roque
        if (!hasMoved && !ChessPanel.isKingInCheck(this.isWhite, board)) {
            // Petit roque
            Piece rook1 = board[row][7];
            if (rook1 instanceof Rook && !rook1.hasMoved && board[row][5] == null && board[row][6] == null) {
                if (!isSquareAttacked(row, 5, board) && !isSquareAttacked(row, 6, board)) {
                    moves.add(new Point(row, 6));
                }
            }
            // Grand roque
            Piece rook2 = board[row][0];
            if (rook2 instanceof Rook && !rook2.hasMoved && board[row][1] == null && board[row][2] == null && board[row][3] == null) {
                if (!isSquareAttacked(row, 2, board) && !isSquareAttacked(row, 3, board)) {
                    moves.add(new Point(row, 2));
                }
            }
        }
        return moves;
    }

    private boolean isSquareAttacked(int r, int c, Piece[][] board) {
        // Vérifie si une pièce adverse peut se déplacer sur la case (r, c)
        for (int row = 0; row < 8; row++) {
            for (int col = 0; col < 8; col++) {
                Piece p = board[row][col]; // This check is simplified and doesn't need to be perfect
                if (p != null && p.isWhite != this.isWhite) {
                    for (Point move : p.getPseudoLegalMoves(board)) {
                        if (move.x == r && move.y == c) {
                            return true;
                        }
                    }
                }
            }
        }
        return false;
    }
}

class Queen extends Piece {
    public Queen(boolean isWhite, int row, int col) {
        super(isWhite, row, col);
    }

    @Override
    String getSymbol() {
        return isWhite ? "♕" : "♛";
    }

    @Override
    List<Point> getPseudoLegalMoves(Piece[][] board) {
        List<Point> moves = new ArrayList<>();
        int[] dRow = {-1, -1, -1, 0, 0, 1, 1, 1};
        int[] dCol = {-1, 0, 1, -1, 1, -1, 0, 1};
        addLineMoves(moves, board, dRow, dCol);
        return moves;
    }
}

/**
 * Gère la communication avec le moteur d'échecs Stockfish.
 */
class StockfishClient {
    private Process process;
    private BufferedReader reader;
    private BufferedWriter writer;

    public StockfishClient() throws IOException {
        // Le chemin vers l'exécutable de Stockfish.
        // Assurez-vous que stockfish.exe est dans le même dossier que le .jar ou le .java
        String stockfishPath = "stockfish.exe";
        if (!new File(stockfishPath).exists()) {
            // Fallback for other OS
            stockfishPath = "stockfish";
        }

        ProcessBuilder builder = new ProcessBuilder(stockfishPath);
        this.process = builder.start();
        this.reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        this.writer = new BufferedWriter(new OutputStreamWriter(process.getOutputStream()));

        // Initialiser le moteur en mode UCI
        sendCommand("uci");
        // Attendre la confirmation "uciok"
        readOutput("uciok");
    }

    public void sendCommand(String command) throws IOException {
        writer.write(command + "\n");
        writer.flush();
    }

    public String readOutput(String stopSignal) throws IOException {
        String line;
        StringBuilder output = new StringBuilder();
        while ((line = reader.readLine()) != null) {
            output.append(line).append("\n");
            if (line.contains(stopSignal)) {
                break;
            }
        }
        return output.toString();
    }

    public String getBestMove(List<String> moves, int skillLevel) throws IOException {
        sendCommand("setoption name Skill Level value " + skillLevel);
        String movesString = String.join(" ", moves);
        sendCommand("position startpos moves " + movesString);

        // Définir un temps de réflexion basé sur la difficulté
        int moveTime = 500 + skillLevel * 100; // De 500ms à 2500ms
        sendCommand("go movetime " + moveTime);

        String output = readOutput("bestmove");
        for (String line : output.split("\n")) {
            if (line.startsWith("bestmove")) {
                return line.split(" ")[1];
            }
        }
        return null;
    }

    public void sendUciNewGame() { try { sendCommand("ucinewgame"); } catch (IOException e) { e.printStackTrace(); } }

    public void close() {
        try { sendCommand("quit"); } catch (IOException e) { e.printStackTrace(); }
        process.destroy();
    }
}

class Rook extends Piece {
    public Rook(boolean isWhite, int row, int col) {
        super(isWhite, row, col);
    }

    @Override
    String getSymbol() {
        return isWhite ? "♖" : "♜";
    }

    @Override
    List<Point> getPseudoLegalMoves(Piece[][] board) {
        List<Point> moves = new ArrayList<>();
        int[] dRow = {-1, 1, 0, 0};
        int[] dCol = {0, 0, -1, 1};
        addLineMoves(moves, board, dRow, dCol);
        return moves;
    }
}

class Bishop extends Piece {
    public Bishop(boolean isWhite, int row, int col) {
        super(isWhite, row, col);
    }

    @Override
    String getSymbol() {
        return isWhite ? "♗" : "♝";
    }

    @Override
    List<Point> getPseudoLegalMoves(Piece[][] board) {
        List<Point> moves = new ArrayList<>();
        int[] dRow = {-1, -1, 1, 1};
        int[] dCol = {-1, 1, -1, 1};
        addLineMoves(moves, board, dRow, dCol);
        return moves;
    }
}

class Knight extends Piece {
    public Knight(boolean isWhite, int row, int col) {
        super(isWhite, row, col);
    }

    @Override
    String getSymbol() {
        return isWhite ? "♘" : "♞";
    }

    @Override
    List<Point> getPseudoLegalMoves(Piece[][] board) {
        List<Point> moves = new ArrayList<>();
        int[] dRow = {-2, -2, -1, -1, 1, 1, 2, 2};
        int[] dCol = {-1, 1, -2, 2, -2, 2, -1, 1};

        for (int i = 0; i < 8; i++) {
            int newRow = row + dRow[i];
            int newCol = col + dCol[i];
            if (isValid(newRow, newCol)) {
                Piece target = board[newRow][newCol];
                if (target == null || target.isWhite != this.isWhite) {
                    moves.add(new Point(newRow, newCol));
                }
            }
        }
        return moves;
    }
}

class Pawn extends Piece {
    boolean enPassantVulnerable = false;

    public Pawn(boolean isWhite, int row, int col) {
        super(isWhite, row, col);
    }

    @Override
    String getSymbol() {
        return isWhite ? "♙" : "♟";
    }

    @Override
    List<Point> getPseudoLegalMoves(Piece[][] board) {
        List<Point> moves = new ArrayList<>();
        int direction = isWhite ? -1 : 1;

        // Avancer d'une case
        int oneStepRow = row + direction;
        if (isValid(oneStepRow, col) && board[oneStepRow][col] == null) {
            moves.add(new Point(oneStepRow, col));

            // Avancer de deux cases (premier coup)
            int twoStepsRow = row + 2 * direction;
            if (!hasMoved && isValid(twoStepsRow, col) && board[twoStepsRow][col] == null) {
                moves.add(new Point(twoStepsRow, col));
            }
        }

        // Captures en diagonale
        int[] dCol = {-1, 1};
        for (int dc : dCol) {
            int newRow = row + direction;
            int newCol = col + dc;
            if (isValid(newRow, newCol)) {
                Piece target = board[newRow][newCol];
                if (target != null && target.isWhite != this.isWhite) {
                    moves.add(new Point(newRow, newCol));
                }
            }
        }

        // Prise "en passant"
        for (int dc : dCol) {
            int newCol = col + dc;
            if (isValid(row, newCol)) {
                Piece adjacentPiece = board[row][newCol];
                if (adjacentPiece instanceof Pawn && adjacentPiece.isWhite != this.isWhite && ((Pawn) adjacentPiece).enPassantVulnerable) {
                    moves.add(new Point(row + direction, newCol));
                }
            }
        }

        return moves;
    }
}